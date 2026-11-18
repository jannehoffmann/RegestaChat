import os
from pathlib import Path

from dotenv import load_dotenv

import httpx
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

# FastMCP-Client für die Kommunikation mit dem Neo4j-Datenbankserver über den offiziellen Neo4j-MCP-Server.

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

MCP_URL = os.getenv("MCP_URL")
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

class Neo4jMCPClient:
    # Initialisierung des FastMCP-Clients mit den erforderlichen Transport- und Authentifizierungsinformationen.
    def __init__(self):
        transport = StreamableHttpTransport(
            url=MCP_URL,
            headers={
                "X-Neo4j-MCP-URI": NEO4J_URI,
            },
            auth=httpx.BasicAuth(
                NEO4J_USER,
                NEO4J_PASSWORD,
            ),
        )

        self.client = Client(transport)

    # Asynchrone Methode zum Abrufen der Liste der verfügbaren Tools vom MCP-Server.
    async def list_tools(self):
        async with self.client:
            tools = await self.client.list_tools()
            return [
                {
                    "name": tool.name,
                    "description": tool.description,
                }
                for tool in tools
            ]

    # Asynchrone Methode zum Abrufen des Neo4j-Datenbankschemas vom MCP-Server.
    async def get_schema(self):
        async with self.client:
            result = await self.client.call_tool(
                "get-schema",
                {})
            return result.content

    # Asynchrone Methode zum Ausführen von lesenden Cypher-Abfragen auf der Neo4j-Datenbank über den MCP-Server.
    async def read_cypher(self, query: str):
        async with self.client:
            result = await self.client.call_tool(
                "read-cypher",
                {"query": query},
            )
            return result.content
        
    # Asynchrone Methode zum Ausführen von schreibenden Cypher-Abfragen auf der Neo4j-Datenbank über den MCP-Server. (wird derzeit nicht verwendet, aber für zukünftige Erweiterungen bereitgestellt)
    async def write_cypher(self, query: str):
        async with self.client:
            result = await self.client.call_tool(
                "write-cypher",
                {"query": query},
            )
            return result.content

# Instanz des Neo4jMCPClient erstellen, die im gesamten Backend verwendet wird.
neo4j_mcp = Neo4jMCPClient()