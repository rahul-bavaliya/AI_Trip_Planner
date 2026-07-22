
"""A class to build a graph from nodes and edges."""
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.state import CompiledStateGraph

from prompt_library.prompt import SYSTEM_PROMPT
from utils.model_loader import ModelLoader


class GraphBuilder():
    
    """Initializes the GraphBuilder with a graph object."""
    def __init__(self, model_provider:str = "groq"):
        self.model_loader = ModelLoader(model_provider=model_provider)
        self.llm = self.model_loader.load_llm()
        
        self.tools = []
        
        self.weather_info_tools = WeatherInfoTool()
        self.place_search_tools = PlaceSearchTool()
        self.calculator_tools = CalculatorTool()
        self.currency_converter_tools = CurrencyConverterTool()
        
        self.tools.extend([* self.weather_info_tools.weather_tool_list, 
                           * self.place_search_tools.place_search_tool_list,
                           * self.calculator_tools.calculator_tool_list,
                           * self.currency_converter_tools.currency_converter_tool_list])
        
        self.llm_with_tools = self.llm.bind_tools(tools=self.tools)
        
        self.graph = None
        
        self.system_prompt = SYSTEM_PROMPT
        

    """Builds a graph from the given nodes and edges."""
    def build_graph(self) -> CompiledStateGraph:
        """Builds and compiles a state graph with agentic tool routing."""
        graph_builder = StateGraph(MessagesState)

        # 1. Add Nodes (Unified node name to "tools")
        graph_builder.add_node("agent", self.agent_function)
        graph_builder.add_node("tools", ToolNode(tools=self.tools))

        # 2. Flow Edges
        graph_builder.add_edge(START, "agent")
        
        # tools_condition handles routing to 'tools' or END automatically
        graph_builder.add_conditional_edges("agent", tools_condition)
        
        # Pass tool outputs back to agent
        graph_builder.add_edge("tools", "agent")
        
        # 3. End Edge
        graph_builder.add_edge("agent",END)

        # Compile and store
        self.graph = graph_builder.compile()
        
        return self.graph
        

    def agent_function(self, state: MessagesState) -> dict:
        """  Defines the agent's function to process input and decide on tool usage."""
        user_question = state["messages"]
        input_question = [self.system_prompt] + user_question
        llm_response = self.llm_with_tools.invoke(input_question)
        return {"messages": llm_response}
    
    
    def __call__(self):
        """Allows the GraphBuilder instance to be called directly to build the graph."""
        return self.build_graph()