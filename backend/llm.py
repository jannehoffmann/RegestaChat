from collections.abc import AsyncIterator
from typing import Literal, TypedDict
from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
import os
from pathlib import Path
from dotenv import load_dotenv

# Skript für die Kommunikation mit dem LLM über die Ollama-API.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

MODEL_NAME = os.getenv("MODEL_NAME", "qwen3:8b")

# Typdefinition für Nachrichten, die an das LLM gesendet werden. Jede Nachricht hat eine Rolle (system, user oder assistant) und den Inhalt der Nachricht.
class Message(TypedDict):
    role: Literal["system", "user", "assistant"]
    content: str

# Asynchrone Funktion, die eine Liste von Nachrichten an das LLM sendet und die Antwort in Form eines asynchronen Iterators von Textchunks zurückgibt.
async def stream_chat(messages: list[Message]) -> AsyncIterator[str]:
    # Initialisierung des ChatOllama-Modells mit dem in der .env-Datei angegebenen Modellnamen.
    llm = ChatOllama(model=MODEL_NAME)

    langchain_messages = []

    # Konvertierung der Nachrichten in das Format, das von LangChain erwartet wird (SystemMessage, HumanMessage, AIMessage).
    for message in messages:
        if message["role"] == "system":
            langchain_messages.append(SystemMessage(message["content"]))
        elif message["role"] == "assistant":
            langchain_messages.append(AIMessage(message["content"]))
        else:
            langchain_messages.append(HumanMessage(message["content"]))

    # Asynchrone Iteration über die vom LLM gestreamten Antworten.
    async for chunk in llm.astream(langchain_messages):
        if isinstance(chunk.content, str):
            yield chunk.content
        elif isinstance(chunk.content, list):
            for block in chunk.content:
                if isinstance(block, dict) and isinstance(block.get("text"), str):
                    yield block["text"]