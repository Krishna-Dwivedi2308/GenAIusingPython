from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.mongodb import MongoDBSaver
from langchain_core.messages import HumanMessage
from langgraph.types import interrupt, Command
from dotenv import load_dotenv
import json

load_dotenv()


@tool()
def human_interruption(query: str) -> str:
    """request assistance from human"""
    human_message = interrupt(
        {"query": query}
    )  # this saves the state in db and kills the graph
    return human_message["data"]


# now the problem will be kept in db until the human send a response himself.
# when , they have sent the response the graph will resume from there

tools = [human_interruption]


class State(TypedDict):
    messages: Annotated[list, add_messages]


llm = init_chat_model(model_provider="openai", model="gpt-4.1")
llm_with_tools = llm.bind_tools(tools)


def chat_bot(state: State):
    messages = llm_with_tools.invoke(state["messages"])
    return {"messages": [messages]}


graph_builder = StateGraph(State)

tool_node = ToolNode(tools=tools)

graph_builder.add_node("chat_bot", chat_bot)
graph_builder.add_node("tools", tool_node)

graph_builder.add_edge(START, "chat_bot")
graph_builder.add_conditional_edges("chat_bot", tools_condition)
graph_builder.add_edge("tools", "chat_bot")
graph_builder.add_edge("chat_bot", END)


# persistence or checkpointing
def create_chat_graph(checkpointer):
    return graph_builder.compile(checkpointer=checkpointer)


def user_chat():

    DB_URI = "mongodb://admin:secret@localhost:27017"
    config = {"configurable": {"thread_id": "1"}}
    with MongoDBSaver.from_conn_string(DB_URI) as checkpointer:
        graph_with_mongo = create_chat_graph(checkpointer)

        while True:
            user = input("User> ")
            _state = State(messages=[HumanMessage(content=user)])
            # a fresh new state created here
            for event in graph_with_mongo.stream(
                _state, config=config, stream_mode="values"
            ):
                if "messages" in event:
                    event["messages"][-1].pretty_print()

        # invoke end - state is deleted .Only result will print. The messages are lost now - if we want to get old context , we can't.even putting while loop in main function will not work here . because invoke will  delete the state annyways in every iteration .


# user_chat()


def admin_call():

    DB_URI = "mongodb://admin:secret@localhost:27017"
    config = {"configurable": {"thread_id": "1"}}
    with MongoDBSaver.from_conn_string(DB_URI) as checkpointer:
        graph_with_mongo = create_chat_graph(checkpointer)

        state = graph_with_mongo.get_state(config=config)
        last_message = state.values["messages"][-1]
        # now this last message can be a simple message from uuser or can be an interrupt
        # we are intterested in interrupt only

        # below code is from documentation
        tool_calls = last_message.additional_kwargs.get("tool_calls", [])

        user_query = None

        for call in tool_calls:
            if call.get("function", {}).get("name") == "human_interruption":
                args = call["function"].get("arguments", {})
                try:
                    args_dict = json.loads(args)
                    user_query = args_dict.get("query")
                except json.JSONDecodeError:
                    print("failed to decode function arguments")
        print("user has a query ", user_query)
        solution = input("Admin> ")
        resume_command = Command(resume={"data": solution})

        for event in graph_with_mongo.stream(
            resume_command, config, stream_mode="values"
        ):
            if "messages" in event:
                event["messages"][-1].pretty_print()


admin_call()
