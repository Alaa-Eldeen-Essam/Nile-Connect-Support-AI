# Nile Connect Support AI

A Dockerized FastAPI and React portfolio project extracted from the original LangChain notebook. It demonstrates a tool-calling customer-support agent with Gemini, Retrieval-Augmented Generation (RAG), profile validation, support tickets, and persisted chat history.

> Independent educational demonstration. Nile Connect Support AI is not affiliated with, endorsed by, or operated by Telecom Egypt, WE, or another telecom provider. The demonstration knowledge base is adapted from the public Kaggle dataset [WE Telecom Scraped Data](https://www.kaggle.com/datasets/mahmoudramadan025/we-telecom-scraped-data); it may be incomplete or inaccurate. Do not enter real customer, billing, or account data.

## Features

- Premium single-screen React chat interface with a mobile layout and suggestion prompts.
- Gemini tool-calling agent built from the original notebook logic.
- RAG search over bundled Markdown demonstration content using Qdrant.
- Egyptian phone and age validation with Pydantic.
- SQLite profiles locally; MongoDB profiles for the hosted deployment.
- MongoDB ticket and chat-history storage.
- Protected admin settings drawer with encrypted runtime integration settings.
- Docker Compose local stack and a Render deployment blueprint.

## Architecture

```text
Browser → FastAPI controllers → LangChain services → SQLite/MongoDB/Qdrant repositories
```

The controller layer owns HTTP requests, templates are the view layer, and repositories isolate persistence. The Gemini prompt, three original tools, Qdrant retrieval, MongoDB history, and ticket workflow remain in the agent service.

## Run locally with Docker

1. Copy `.env.example` to `.env`.
2. Add `GOOGLE_API_KEY`.
   Keep `QDRANT_API_KEY` empty when using the included local Docker Qdrant service.
   Set both `QDRANT_URL` and `QDRANT_API_KEY` only when switching to Qdrant Cloud.
3. Generate settings secrets if you want the admin settings page:

   ```bash
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```

4. Start the complete stack:

   ```bash
   docker compose up --build
   ```

5. Open `http://localhost:8000`.

The first agent request creates a missing Qdrant collection from `knowledge_base/`. You can also run ingestion directly:

```bash
docker compose run --rm web python scripts/ingest_knowledge_base.py
```

## Runtime settings

Open the `•••` menu in the app, choose **Admin settings**, and enter `SETTINGS_ADMIN_TOKEN`. Gemini and optional Qdrant values are encrypted in MongoDB and never returned to the browser. The entered token stays only in browser memory. `MONGO_URI` remains a deployment secret so the settings store is available after a restart.

## Deploy on Render

1. Create a MongoDB Atlas Free cluster and database user.
2. Create a Render Web Service from this GitHub repository; `render.yaml` is included.
3. Add `GOOGLE_API_KEY`, `MONGO_URI`, `SETTINGS_ENCRYPTION_KEY`, and `SETTINGS_ADMIN_TOKEN` in Render’s secret environment-variable screen.
4. Deploy and check `/healthz`.

Render’s free web service may sleep after 15 minutes of inactivity and its disk is temporary, so the hosted profile/history/ticket data is stored in MongoDB. See [Render’s free-service limits](https://render.com/docs/free). MongoDB Atlas Free clusters are documented as non-expiring, although idle clusters can pause. See [MongoDB’s Atlas Free documentation](https://www.mongodb.com/docs/atlas/tutorial/deploy-free-tier-cluster/).

No free provider can guarantee lifetime, always-on Docker compute and persistence without conditions. This project is designed for a no-subscription portfolio deployment under the current free-tier limits.

## Verification

```bash
pip install ".[dev]"
ruff check .
pytest
docker build -t we-telecom-agent .
```

## Project structure

```text
app/controllers  HTTP endpoints
app/models       Pydantic schemas
app/repositories SQLite and MongoDB persistence
app/services     LangChain agent, RAG, and runtime settings
frontend/        React showcase interface and settings drawer
```
