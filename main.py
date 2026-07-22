import os

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from agent.agentic_worlflow import GraphBuilder


app = FastAPI()


class QueryRequest(BaseModel):
    query: str
    def __init__(self, query: str):
        self.query = query
        
@app.post("/query")
async def query_travel_agent(query: QueryRequest):
    try:
        # Print the received query for debugging purposes
        print(f"Received query: {query.query}")
        
        # Here generate the GraphBuilder
        graph = GraphBuilder(model_provider="groq")
        react_app = graph()
        
        png_graph = react_app.get_graph().draw_mermaid_png()
        with open("my_graph.png", "wb") as f:
            f.write(png_graph)
            
        print(f"Graph generated and saved as my_graph.png in {os.getcwd()}")
        
        # Assuming request is a pydantic object like: {"question": "What is the weather in Paris?"}
        messages = {"messages": [query.question]}
        
        # Output from the react app
        output = react_app.invoke(messages)
        
        # If result is dict with messages:
        if isinstance(output, dict) and "messages" in output:
            final_response =  output["messages"][-1]  # Get the last message from the list
        else:
            final_response = str(output)  # Convert to string if not in expected format
            
        return {"answer": final_response}
    except Exception as e:
        print(f"Error processing query: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})