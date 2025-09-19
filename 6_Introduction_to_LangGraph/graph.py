from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

# from typing_extensions import TypedDict

# from langgraph.graph.message import add_messages

"""
# this code below is from official documantation
class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)
"""


class State(TypedDict):
    query: str
    llm_result: str | None


# now let us create a node which is basically a function
def chat_bot(state: State):
    query = state["query"]
    # here we write our code for the bussiness problem
    completion = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "user",
                "content": query,
            },
        ],
    )
    result = completion.choices[0].message.content
    state["llm_result"] = result  # state updation
    return state


graph_builder = StateGraph(State)

graph_builder.add_node("chat_bot", chat_bot)

graph_builder.add_edge(START, "chat_bot")
graph_builder.add_edge("chat_bot", END)

graph = graph_builder.compile()


def main():
    user = input("user:")
    _state = {"query": user, "llm_result": None}
    # invoke the graph
    graph_result = graph.invoke(_state)
    print(graph_result)

    # print(graph)


if __name__ == "__main__":
    main()
