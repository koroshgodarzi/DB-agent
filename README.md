## db-agent

An LLM-powered SQL agent that lets you query a PostgreSQL database using natural language.

The service exposes a simple FastAPI endpoint that:
- **Takes a user question** in plain English
- **Uses LangGraph + LangChain + Ollama** to generate a PostgreSQL query based on a JSON schema
- **Executes the SQL read-only against Postgres**
- **Returns both the raw rows and a human-friendly summary** of the result

This is ideal as a backend component for analytics assistants, BI copilots, or internal data tools that need safe, explainable database access.

---

## Tech Stack

- **Backend framework**: `FastAPI`
- **Orchestration / agent framework**: `LangGraph` (graph-based workflow for the agent)
- **LLM integration**: `LangChain` + `langchain-ollama` (talking to a local Ollama server)
- **Database & ORM**:
  - `PostgreSQL`
  - `SQLAlchemy` for models and DB access
  - `psycopg2` as the Postgres driver
- **Web server**: `uvicorn`
- **Configuration**: `python-dotenv` (`dotenv`)
- **Containerization & services**: `Docker`, `docker-compose`
- **(Optional in compose)**: `qdrant` vector DB (service is defined in `docker-compose.yml` but not required for basic SQL agent functionality)

Project dependencies are defined in `pyproject.toml`.

---

## High-Level Architecture

- **`agent/`**
  - `generate_sql_query.py`: Uses `OllamaLLM` (LangChain + Ollama) and `schema.json` to turn natural language into SQL.
  - `run_sql_query.py`: Executes read-only SQL queries against PostgreSQL.
- **`graph/`**
  - `workflow.py`: LangGraph workflow with the following nodes:
    - Retrieve DB schema context
    - Generate SQL query
    - Execute SQL query
    - Generate final response / summary
- **`database/`**
  - Database models, sample data, and simple DB views/tools.
- **`main.py`**
  - Defines the FastAPI app and `/chat/{session_id}` endpoint that runs the workflow and stores per-session state.
- **`docker-compose.yml`**
  - Brings up `postgres`, `qdrant`, `ollama`, and the `fastapi` service.

---

## API Overview

- **Endpoint**: `POST /chat/{session_id}`
- **Query params/body**: `message` (string) – the user’s natural language question.
- **Response**: JSON containing:
  - `chat_history`: list of user messages
  - `workflow_history`: LangGraph node history / reasoning steps
  - `user_query`: last user question
  - `sql_query`: generated SQL statement
  - `query_results`: list of row objects from PostgreSQL
  - `final_response`: human-readable answer summarizing the results

Each `session_id` keeps its own conversational state in memory (for this process).

---

## Prerequisites

- **Docker & Docker Compose** installed
- **Python 3.10+** (only needed if you want to run without Docker)
- **Ollama model**:
  - The default model used in `agent/generate_sql_query.py` is:
    - `mannix/defog-llama3-sqlcoder-8b`
  - Make sure this model is available to your Ollama instance (e.g. `ollama pull mannix/defog-llama3-sqlcoder-8b` inside the `ollama` container or your local environment).

---

## Environment Variables

The `docker-compose.yml` expects the following environment variables (e.g. in a `.env` file in the project root or exported in your shell):

- **`POSTGRES_USER`**: Postgres username
- **`POSTGRES_PASSWORD`**: Postgres password
- **`POSTGRES_DB`**: Database name

The `fastapi` container also uses:

- **`OLLAMA_BASE_URL`**:
  - Set via compose to `http://ollama:11434` (service name from `docker-compose.yml`).
  - When running locally without Docker, defaults to `http://localhost:11434`.

You can also configure additional environment variables for local DB connection in the database utilities if needed.

---

## Running with Docker (Recommended)

1. **Create a `.env` file** in the project root:

```bash
cat > .env << 'EOF'
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=db_agent
EOF
```

2. **Start the full stack** (Postgres, Qdrant, Ollama, FastAPI):

```bash
docker compose up --build
docker compose exec ollama ollama pull mannix/defog-llama3-sqlcoder-8b
```

This will:
- Start **PostgreSQL** on port `5432`
- Start **Qdrant** on port `6333`
- Start **Ollama** on port `11434`
- Build and start the **FastAPI** app on port `80`

3. **Access the API docs** (once containers are healthy):

- Open: `http://localhost/docs`  (FastAPI Swagger UI)
- Test the `POST /chat/{session_id}` endpoint by passing a `message` query parameter (e.g. `"Show me all products in the Electronics category"`).

To stop the stack:

```bash
docker compose down
```

---

## Running Locally Without Docker

1. **Create and activate a virtual environment** (optional but recommended):

```bash
python -m venv .venv
source .venv/bin/activate  # on macOS / Linux
# .venv\Scripts\activate   # on Windows (PowerShell or cmd)
```

2. **Install dependencies** from `pyproject.toml` (using `pip` + `pip-tools`-style or `uv`/`pip`):

If you have `uv`:

```bash
uv sync
```

Or with plain `pip`:

```bash
pip install -e .
```

3. **Run Postgres**:
   - Either:
     - Use a local Postgres instance and configure the same DB as in `database/database_models.py`, or
     - Run only the Postgres container:

```bash
docker compose up postgres -d
```

4. **Make sure Ollama is running locally**:

```bash
ollama serve
ollama pull mannix/defog-llama3-sqlcoder-8b
```

Ensure `OLLAMA_BASE_URL` is set appropriately (defaults to `http://localhost:11434`).

5. **Start the FastAPI app**:

```bash
uvicorn main:app --reload --port 8000
```

Then open `http://localhost:8000/docs` to try the `/chat/{session_id}` endpoint.

---

## Development Notes

- **Schema-driven generation**:
  - The agent reads `agent/schema.json` to understand the DB structure, relationships, and business logic.
  - Update this file when your DB schema changes so the LLM generates valid SQL.
- **Read-only queries**:
  - `execute_readonly_query` is designed for safe, SELECT-style queries; extending to mutations should be done carefully.
- **Extending the agent**:
  - You can add new nodes to `graph/workflow.py` (e.g. for caching, additional validation, or result post-processing).
  - You can swap the Ollama model or adjust prompts in `agent/generate_sql_query.py` to better fit your domain.

---


