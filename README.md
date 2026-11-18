# RegestaChat

RegestaChat ist ein Webapp mit einem lokalen Chatbot, welcher ausschließlich anhand von Daten aus einer lokalen Neo4j-Datenbank antwortet.

Die Anwendung verwendet:

- FastAPI für die HTTP-Endpunkte
- Neo4j und Neo4j-MCP als Docker-Container
- Ollama mit einem lokalen LLM
- LangChain für die Kommunikation mit Ollama
- Streamlit als einfaches Frontend

## Voraussetzungen

- Python 3.12 oder neuer
- Docker mit Docker Compose
- Ollama

Prüfe die Installation:

```bash
python --version
docker --version
docker compose version
ollama --version
```

## Projektstruktur

```text
.
├── backend/
│   ├── main.py
│   ├── chat_service.py
│   ├── llm.py
│   ├── mcp_client.py
│   └── requirements.txt
├── frontend/
│   ├── app.py
│   └── requirements.txt
├── docker-compose.yml
├── .env
└── README.md
```

## 1. Repository vorbereiten

Wechsle in das Projektverzeichnis.

## 2. `.env`-Datei erstellen

Die Anwendung liest ihre Konfiguration aus einer `.env`-Datei im Projektwurzelverzeichnis.

Erstelle die Datei:

```bash
touch .env
```

Beispielinhalt:

```dotenv
NEO4J_PASSWORD=dein-sicheres-passwort
NEO4J_DATABASE=neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j

MCP_URL=http://localhost:8080/mcp
MODEL_NAME=qwen3:8b
```

Die Werte `NEO4J_PASSWORD`, `NEO4J_DATABASE`, `NEO4J_URI`, `NEO4J_USER`, `MCP_URL` und `MODEL_NAME` müssen zu deiner lokalen Installation passen.

Wichtig:

- Verwende für Neo4j ein sicheres Passwort.
- Committe die `.env`-Datei nicht in Git.
- Die `.env`-Datei ist bereits in der `.gitignore` enthalten.
- Die Werte in `docker-compose.yml` und `.env` müssen zusammenpassen.

## 3. Neo4j und Neo4j-MCP mit Docker starten

Starte Neo4j und den Neo4j-MCP-Server aus dem Projektwurzelverzeichnis:

```bash
docker compose up -d
```

Docker startet:

- Neo4j auf `http://localhost:7474`
- Neo4j Bolt auf `bolt://localhost:7687`
- Neo4j-MCP auf `http://localhost:8080`

Prüfe, ob beide Container laufen:

```bash
docker compose ps
```

Optional können die Container-Logs geprüft werden:

```bash
docker compose logs -f neo4j
docker compose logs -f neo4j-mcp
```

Die Dienste können mit folgendem Befehl beendet werden:

```bash
docker compose down
```

Die Datenbankdaten bleiben durch die Docker-Volumes `neo4j_data` und `neo4j_logs` erhalten.

## 4. Ollama vorbereiten

Starte Ollama per Doppelklick auf die Ollama Anwendung. 

Lade das in `.env` konfigurierte Modell herunter:

```bash
ollama pull qwen3:8b
```

Wenn ein anderes Modell verwendet werden soll, ändere `MODEL_NAME` in der `.env`-Datei und lade dieses Modell vorher mit `ollama pull`.

Prüfe verfügbare Modelle:

```bash
ollama list
```

## 5. Python-Abhängigkeiten installieren

Am einfachsten werden Backend und Frontend in derselben virtuellen Umgebung installiert:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
python -m pip install -r frontend/requirements.txt
```

## 6. Backend starten

Öffne ein Terminal und starte das FastAPI-Backend:

```bash
cd backend
source .venv/bin/activate
uvicorn main:app --reload --port 8000
```

Das Backend ist anschließend erreichbar unter:

- API: `http://127.0.0.1:8000`
- Swagger-Dokumentation: `http://127.0.0.1:8000/docs`
- Health-Check: `http://127.0.0.1:8000/health`

Das Backend muss laufen, bevor das Frontend eine Chatnachricht senden kann.

## 7. Frontend starten

Öffne ein weiteres Terminal und starte Streamlit:

```bash
source .venv/bin/activate
cd frontend
streamlit run app.py
```

Streamlit öffnet die Anwendung normalerweise unter:

```text
http://localhost:8501
```

## 8. Anwendung testen

Teste zuerst Neo4j und MCP:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/mcp/tools
curl http://127.0.0.1:8000/graph/schema
```

Danach kann die Anwendung über Streamlit unter `http://localhost:8501` verwendet werden.
