from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.mongodb import MongoDBSaver

from dotenv import load_dotenv

load_dotenv()


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


# now here we will use iangchain abstraction of llm
llm = init_chat_model(model_provider="openai", model="gpt-4.1")


def chat_node(state: State):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


graph_builder = StateGraph(State)
graph_builder.add_node("chat_node", chat_node)

graph_builder.add_edge(START, "chat_node")
graph_builder.add_edge("chat_node", END)

# we would compile here if we don't want to use mongodb for checkpointing
# graph=graph_builder.compile()


def compile_graph_with_checkpointer(checkpointer):
    graph_with_checkpointer = graph_builder.compile(checkpointer=checkpointer)
    return graph_with_checkpointer


def main():
    user = input("User> ")
    DB_URI = "mongodb://admin:secret@localhost:27017"
    config = {"configurable": {"thread_id": "1"}}
    with MongoDBSaver.from_conn_string(DB_URI) as checkpointer:
        graph_with_mongo = compile_graph_with_checkpointer(checkpointer)
        _state = {"messages": [{"role": "user", "content": user}]}
        # a fresh new state created here
        result = graph_with_mongo.invoke(_state, config)
        # invoke end - state is deleted .Only result will print. The messages are lost now - if we want to get old context , we can't.even putting while loop in main function will not work here . because invoke will  delete the state annyways in every iteration .
        print(result)


main()
