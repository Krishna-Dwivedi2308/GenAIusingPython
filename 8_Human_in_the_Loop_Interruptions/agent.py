from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
import requests
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()


class State(TypedDict):
    messages: Annotated[list, add_messages]


# create a tool for getting the weather
@tool()
def get_weather(city: str):
    """This tool return the weather in a city from the website wttr.in"""
    url = f"http://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)
    if response.status_code == 200:
        return f"The weather in {city} is {response.text}"
    return "something went wrong"


@tool()
def add_two_numbers(a: int, b: int):
    """This tool adds two int numbers"""
    return a + b


# create a list of tools
tools = [get_weather, add_two_numbers]
# init the llm
llm = init_chat_model(model_provider="openai", model="gpt-4.1")
# bind the tools with the llm
llm_with_tools = llm.bind_tools(tools)
# note that if we invoke using llm it does not have the tools attached to it
# but if we invoke using llm_with_tools it has the tools attached to it


def chat_bot(state: State):
    messages = llm_with_tools.invoke(state["messages"])
    return {"messages": messages}


# ============================
# HYBRID WORKFLOW
# ============================


# create and compile the graph
tool_node = ToolNode(tools=tools)

graph_builder = StateGraph(State)

graph_builder.add_node("chat_bot", chat_bot)
graph_builder.add_node("tools", tool_node)

graph_builder.add_edge(START, "chat_bot")
graph_builder.add_conditional_edges("chat_bot", tools_condition)
graph_builder.add_edge("tools", "chat_bot")


graph = graph_builder.compile()


# main function to inkvoke/stream the graph
def main():
    user = input("user: ")
    _state = {"messages": [{"role": "user", "content": user}]}
    # invoke the graph
    for event in graph.stream(_state, stream_mode="values"):
        if "messages" in event:
            event["messages"][-1].pretty_print()


main()

# ========================================
# THIS DOES NOT HAVE HUMAN IN THE LOOP YET
# ========================================
