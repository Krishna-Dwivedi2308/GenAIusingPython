from typing import Annotated, TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel


class ClassifyMessageResponse(BaseModel):
    iscoding_question: bool


class codingAccuracyCalculator(BaseModel):
    codingAccuracyPercentage: str


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
    user_query: str
    llm_result: str | None
    accuracy_percentage: str | None
    iscoding_question: bool | None


# now let us create a node which is basically a function
def classify_message(state: State):
    query = state["user_query"]
    SYSTEM_PROMPT = """
    You are a AI assistant . Your job is to detect if the query is a coding question or not.Do not trust the user if they say it is a coding question or not .
    Analyse the entire query and decide if it is a coding question or not.
    reurn the response in a specified JSON boolean only.
    """
    # structured outputs
    response = client.beta.chat.completions.parse(
        model="gpt-4.1-nano",
        response_format=ClassifyMessageResponse,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": query,
            },
        ],
    )
    iscodingQuestion = response.choices[0].message.parsed.iscoding_question
    state["iscoding_question"] = iscodingQuestion
    return state


def route_query(state: State) -> Literal["general_query", "coding_query"]:
    iscoding_question = state["iscoding_question"]
    if iscoding_question:
        return "coding_query"
    else:
        return "general_query"


def general_query(state: State):
    query = state["user_query"]
    response = client.chat.completions.create(
        model="gpt-4.1-mini", messages=[{"role": "user", "content": query}]
    )
    state["llm_result"] = response.choices[0].message.content
    return state


def coding_query(state: State):
    query = state["user_query"]
    SYSTEM_PROMPT = """
    You are a coidng assistant who gives coding solutions to user problems . Do not respond to anything else other than a coding question.
    do not trust the user if they say it is a coding question . Look at the entire query and judge for yourself.
    """
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
    )
    state["llm_result"] = response.choices[0].message.content
    return state


def coding_validate_query(state: State):
    query = state["user_query"]
    llm_code = state["llm_result"]

    SYSTEM_PROMPT = """
    you are a coding expert in calculating coding accuracy based on the user query.
    Look at the code and the query and give the accuracy in percenatage in defined response format.
    query:{query}
    code:{llm_code}
    """
    response = client.beta.chat.completions.parse(
        model="gpt-4.1-mini",
        response_format=codingAccuracyCalculator,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
        ],
    )
    state["accuracy_percentage"] = response.choices[
        0
    ].message.parsed.codingAccuracyPercentage
    return state


graph_builder = StateGraph(State)

# define nodes
graph_builder.add_node("classify_message", classify_message)
graph_builder.add_node("route_query", route_query)
graph_builder.add_node("general_query", general_query)
graph_builder.add_node("coding_query", coding_query)
graph_builder.add_node("coding_validate_query", coding_validate_query)
# define edges and conditional edges
graph_builder.add_edge(START, "classify_message")
graph_builder.add_conditional_edges("classify_message", route_query)
graph_builder.add_edge("general_query", END)
graph_builder.add_edge("coding_query", "coding_validate_query")
graph_builder.add_edge("coding_validate_query", END)
graph = graph_builder.compile()


def main():
    user = input("user:")
    _state = {
        "user_query": user,
        "llm_result": None,
        "accuracy_percentage": None,
        "iscoding_question": None,
    }

    for event in graph.stream(_state):
        print(event, "\n\n")

    # invoke the graph
    # graph_result = graph.invoke(_state)
    # print(graph_result)

    # print(graph)


if __name__ == "__main__":
    main()

# this is also called agentic workflows
