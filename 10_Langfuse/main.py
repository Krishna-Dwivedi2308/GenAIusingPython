from langfuse.openai import openai
from dotenv import load_dotenv

load_dotenv()

completion = openai.chat.completions.create(
    name="test-chat",
    model="gpt-4o",
    messages=[
        {
            "role": "system",
            "content": "You are a very accurate calculator. You output only the result of the calculation.",
        },
        {"role": "user", "content": "1 + 1 = "},
    ],
)
print(completion.choices[0].message.content)
