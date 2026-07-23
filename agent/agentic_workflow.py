"""A class to build a graph from nodes and edges with a single weather tool."""

from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from logger.logging import get_logger
from prompt_library.prompt import SYSTEM_PROMPT
from tools.weather_info_tool import WeatherInfoTool
from utils.model_loader import ModelLoader

logger = get_logger(__name__)


class GraphBuilder:

    def __init__(self, model_provider: str = "groq"):
        self.model_loader = ModelLoader(model_provider=model_provider)
        self.llm = self.model_loader.load_llm_model()

        # Load Weather Tool and select strictly ONE tool function
        self.weather_info_tools = WeatherInfoTool()
        
        # Grab the single tool function (e.g. index 0)
        self.single_weather_tool = self.weather_info_tools.weather_tool_list[0]
        
        self.tools = [
            self.single_weather_tool
            ]

        # Bind the single tool to the LLM
        self.llm_with_tools = self.llm.bind_tools(tools=self.tools)
        
        self.graph = None
        self.system_prompt = SYSTEM_PROMPT

    def build_graph(self) -> CompiledStateGraph:
        """Builds and compiles a state graph with agentic tool routing."""
        graph_builder = StateGraph(MessagesState)

        # 1. Add Nodes
        graph_builder.add_node("agent", self.agent_function)
        graph_builder.add_node("tools", ToolNode(tools=self.tools))

        # 2. Add Flow Edges
        graph_builder.add_edge(START, "agent")

        # Automatically routes to 'tools' if the LLM generated a tool call,
        # or routes to END if the LLM produced a final text answer.
        graph_builder.add_conditional_edges("agent", tools_condition)

        # Send tool results back to the agent node
        graph_builder.add_edge("tools", "agent")

        # Compile and store graph
        self.graph = graph_builder.compile()
        return self.graph

    def agent_function(self, state: MessagesState) -> dict:
        """Defines the agent's function to process input and decide on tool usage."""
        user_messages = state["messages"]
        input_messages = [self.system_prompt] + user_messages
        llm_response = self.llm_with_tools.invoke(input_messages)
        return {"messages": [llm_response]}

    def __call__(self):
        return self.build_graph()