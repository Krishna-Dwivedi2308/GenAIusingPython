from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import StateGraph, START, END
import os


@tool
def run_command(name: str):
    """
    Takes a command and runs it on the user's system and gives an output of the command.
    Example: run_command(cmd="ls") will list all the files .
    """
    print("Tool called", name)
    result = os.system(name)
    return result


@tool
def write_file(path: str, content: str):
    """
    Writes content to a file at the given path.
    Creates parent directories if needed.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Wrote content to {path}"


@tool
def read_file(path: str) -> str:
    """
    Reads content from a file at the given path.
    """
    if os.path.isdir(path):
        return f"ERROR: {path} is a directory. Provide a file path."

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


@tool
def search_text(path: str, text: str) -> list[str]:
    """
    Takes a path to a directory and a text string to search for in the files in that directory.
    Returns a list of file paths that contain the text.
    """
    matches = []
    for root, _, files in os.walk(path):
        for file in files:
            full = os.path.join(root, file)
            try:
                with open(full, "r", encoding="utf-8") as f:
                    if text in f.read():
                        matches.append(full)
            except:
                pass
    return matches


available_tools = [run_command, write_file, read_file, search_text]

llm = init_chat_model(model_provider="openai", model="gpt-4.1")
llm_with_tool = llm.bind_tools(tools=available_tools)


class State(TypedDict):
    messages: Annotated[list, add_messages]


def chatbot(state: State):
    SYSTEM_PROMPT = SystemMessage(
        content="""
    You are a powerful agentic AI coding assistant, powered by Claude 3.5 Sonnet. You operate exclusively in Cursor, the world's best IDE.
    Always keep your code in folder called chatgpt. Make sure to generate the folder if not already there .The folder must be definitely generated without asking . The operating system is windows 11 .If a filesystem change is required, you MUST call the appropriate tool.
    Do not describe actions in text.
    Then, each code file must also be creted in the folder and the code must be written in the file.
    After creating the files , write the code in the files. Do not describe actions in text. The code must be surely present in the files .

    """
    )

    message = llm_with_tool.invoke([SYSTEM_PROMPT] + state["messages"])
    return {"messages": [message]}


tool_node = ToolNode(tools=available_tools)

graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()
