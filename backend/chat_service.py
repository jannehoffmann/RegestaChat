from collections.abc import AsyncIterator
from llm import stream_chat
from mcp_client import neo4j_mcp

# Skript für den Chat-Service, der die Kommunikation zwischen dem FastAPI-Server, dem LLM und dem MCP-Client verwaltet.

# Asynchrone Funktion, die eine Benutzerfrage entgegennimmt, das Neo4j-Datenbankschema abruft, eine Cypher-Abfrage generiert,
# diese Abfrage ausführt und schließlich die Antwort an den Benutzer zurückgibt.
async def stream_answer(question: str) -> AsyncIterator[str]:
    # Abrufen des Neo4j-Datenbankschemas über den MCP-Client
    schema = await neo4j_mcp.get_schema()

    # Erstellung der Systemnachricht und der Benutzernachricht für das LLM, um eine Cypher-Abfrage zu generieren, die die Frage des Benutzers beantwortet.
    cypher_messages = [
        {
            "role": "system",
            "content": (
                "Du erzeugst ausschließlich lesende Cypher-Abfragen "
                "für die folgende Neo4j-Datenbank:\n"
                f"{schema}\n"
                "Antworte nur mit der Cypher-Abfrage."
            ),
        },
        {"role": "user", "content": question},
    ]

    # Asynchrone Iteration über die vom LLM gestreamten Cypher-Abfragechunks, um die vollständige Cypher-Abfrage zu erstellen.
    cypher = ""
    async for chunk in stream_chat(cypher_messages):
        cypher += chunk

    # Ausführen der generierten Cypher-Abfrage über den MCP-Client, um die Ergebnisse aus der Neo4j-Datenbank abzurufen.
    result = await neo4j_mcp.read_cypher(cypher)

    # Erstellung der Systemnachricht und der Benutzernachricht für das LLM, um die endgültige Antwort auf die Benutzerfrage basierend auf den Neo4j-Ergebnissen zu generieren.
    answer_messages = [
        {
            "role": "system",
            "content": (
                "Beantworte die Frage des Nutzers anhand der "
                "Neo4j-Ergebnisse. Erfinde keine Daten."
            ),
        },
        {
            "role": "user",
            "content": f"Frage: {question}\nErgebnis: {result}",
        },
    ]

    # Asynchrone Iteration über die vom LLM gestreamten Antwortchunks, um die endgültige Antwort an den Benutzer zu generieren.
    async for chunk in stream_chat(answer_messages):
        yield chunk