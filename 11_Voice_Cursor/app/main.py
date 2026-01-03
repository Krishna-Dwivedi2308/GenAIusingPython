from dotenv import load_dotenv

load_dotenv()

import asyncio
from langchain_core.messages import AIMessage
import speech_recognition as sr
from openai import AsyncOpenAI
from openai.helpers import LocalAudioPlayer
from graph import graph

# Conversation memory
messages = []

# OpenAI async client
openai = AsyncOpenAI()


async def tts(text: str):
    """
    Text-to-Speech using OpenAI streaming audio
    """
    async with openai.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice="nova",
        input=text,
        instructions="Speak in a happy, friendly, and supportive tone",
        response_format="pcm",
    ) as response:
        await LocalAudioPlayer().play(response)


async def main():
    r = sr.Recognizer()

    # Open microphone ONCE
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        r.pause_threshold = 2
        await tts("Hello, how can I help you?")
        while True:
            print("\nListening...")
            audio = r.listen(source)
            print("Recognizing...")

            try:
                stt = r.recognize_google(audio)
                print("You said:", stt)
            except sr.UnknownValueError:
                print("Could not understand audio")
                continue
            except sr.RequestError as e:
                print(f"Speech recognition error: {e}")
                continue

            # Add user message
            messages.append({"role": "user", "content": stt})

            # Run LangGraph
            for event in graph.stream({"messages": messages}, stream_mode="values"):
                if "messages" in event:
                    # reply = event["messages"][-1].content
                    # messages.append(
                    #     {"role": "assistant", "content": reply}
                    # )

                    # event["messages"][-1].pretty_print()

                    # # 🔊 SPEAK AFTER THINKING
                    # await tts(reply)
                    last_msg = event["messages"][-1]

                    # # Only speak AI messages
                    # if last_msg.role == "assistant":
                    #     reply = last_msg.content

                    #     messages.append({
                    #         "role": "assistant",
                    #         "content": reply
                    #     })

                    #     last_msg.pretty_print()
                    #     await tts(reply)
                    last_msg = event["messages"][-1]

                    if isinstance(last_msg, AIMessage):
                        reply = last_msg.content
                        if isinstance(reply, str) and reply.strip():
                            await tts(reply)


if __name__ == "__main__":
    asyncio.run(main())
