from mem0 import Memory
import os
from dotenv import load_dotenv

load_dotenv()
from openai import OpenAI

client = OpenAI()
import json

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


config = {
    "version": "v1.1",
    "embedder": {
        "provider": "openai",
        "config": {
            "api_key": OPENAI_API_KEY,
            "model": "text-embedding-3-small",
        },
    },
    "llm": {
        "provider": "openai",
        "config": {"api_key": OPENAI_API_KEY, "model": "gpt-4.1"},
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {"host": "localhost", "port": "6333"},
    },
    "graph_store": {
        "provider": "neo4j",
        "config": {
            "url": "bolt://localhost:7687",
            "username": "neo4j",
            "password": "reform-william-center-vibrate-press-5829",
        },
    },
}

mem_client = Memory.from_config(config)


def chat():
    while True:
        user_query = input("User> ")
        # all_memories=mem_client.get_all(user_id='piyush')
        relevant_memories = mem_client.search(query=user_query, user_id="piyush")
        memories = [
            f"ID:{mem.get("id")} Memory:{mem.get("memory")}"
            for mem in relevant_memories.get("results")
        ]
        print(memories)
        # print("\n".join(memories))
        SYSTEM_PROMPT = f"""
        you are a memory aware assistant that responds to user queries with context from memory. 
        {json.dumps(memories)}
        """
        print("system : ", SYSTEM_PROMPT)
        result = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_query},
            ],
        )
        print(f"🤖{result.choices[0].message.content}")

        mem_client.add(
            [
                {"role": "user", "content": user_query},
                {"role": "assistant", "content": result.choices[0].message.content},
            ],
            user_id="piyush",
        )


chat()
