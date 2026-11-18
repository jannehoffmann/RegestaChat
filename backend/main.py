from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from mcp_client import neo4j_mcp
from chat_service import stream_answer

# FastAPI-Anwendung für das Backend der Regesta Chat-Anwendung.
# Dieses Skript stellt die Endpunkte bereit, über die das Frontend mit dem Backend kommunizieren kann, um Fragen zu stellen und Antworten zu erhalten.
# Es enthält auch Endpunkte für die Überprüfung des Systemstatus und den Zugriff auf das Neo4j-Datenbankschema.

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

# FastAPI-Anwendung initialisieren
app = FastAPI(
    title="Regesta  Chat Backend",
    version="0.1.0",
)

# Pydantic-Modelle für die Anfragen und Antworten der Endpunkte definieren
class CypherRequest(BaseModel):
    query: str

class CypherResponse(BaseModel):
    query: str
    result: dict | list | str | None

class ChatRequest(BaseModel):
    message: str

# Endpunkt für den Chat mit Streaming-Antworten
@app.post("/chat")
async def chat(request: ChatRequest):
    # Streaming-Antwort vom Chat-Service (Methode stream_answer) zurückgeben
    async def events():
        async for chunk in stream_answer(request.message):
            yield f"data:{chunk}\n\n"

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )

# Endpunkt für die Überprüfung des Systemstatus
@app.get("/health")
async def health():
    return {"status": "ok"}

# Endpunkt für den Zugriff auf die Liste der verfügbaren Tools im MCP-Server
@app.get("/mcp/tools")
async def mcp_tools():
    try:
        return await neo4j_mcp.list_tools()
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"MCP-Server nicht erreichbar: {exc}",
        )

# Endpunkt für den Zugriff auf das Neo4j-Datenbankschema
@app.get("/graph/schema")
async def graph_schema():
    try:
        return await neo4j_mcp.get_schema()
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Neo4j-Schema konnte nicht geladen werden: {exc}",
        )

# Endpunkt für die Ausführung von Cypher-Abfragen auf der Neo4j-Datenbank
@app.post("/graph/read", response_model=CypherResponse)
async def graph_read(request: CypherRequest):
    try:
        result = await neo4j_mcp.read_cypher(request.query)
        return CypherResponse(query=request.query, result=result)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Cypher-Abfrage konnte nicht ausgeführt werden: {exc}",
        )