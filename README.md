# Nile Connect Support AI

A Dockerized FastAPI and React portfolio demonstration extracted from a LangChain support-agent notebook. It uses Gemini tool calling, a Qdrant-backed knowledge base, customer-profile validation, support-request references, and persisted chat history.

> **Independent demonstration:** Nile Connect Support AI is not affiliated with, endorsed by, or operated by Telecom Egypt, WE, or any telecom provider. Its demonstration content is adapted from the public [WE Telecom Scraped Data](https://www.kaggle.com/datasets/mahmoudramadan025/we-telecom-scraped-data) dataset and may be incomplete or inaccurate. Do not enter real personal, account, or billing data.

## What you need

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- A Google Gemini API key for live chat
- Git, if you are cloning the repository

No local Python, Node.js, MongoDB, or Qdrant installation is required.

## Quick start

1. Clone the repository and enter it:

   ```powershell
   git clone <YOUR_REPOSITORY_URL>
   cd WE_agent_portoflio
   ```

2. Create your local secrets file:

   ```powershell
   Copy-Item .env.example .env
   ```

3. Open `.env` and add your Gemini key:

   ```env
   GOOGLE_API_KEY=your_google_gemini_api_key
   ```

4. Start the full application stack:

   ```powershell
   docker compose up --build
   ```

5. Open [http://localhost:8010](http://localhost:8010).

The first chat request initializes the local Qdrant knowledge-base collection, so it can take a little longer than later requests.

Stop the stack with `Ctrl+C`. To run it again in the background, use:

```powershell
docker compose up -d
```

## Configure the optional Settings screen

The hidden **Admin settings** screen can update Gemini and external-Qdrant values while the app is running. It is disabled unless both values below are set in `.env` before starting the stack:

```env
SETTINGS_ENCRYPTION_KEY=replace_with_a_fernet_key
SETTINGS_ADMIN_TOKEN=replace_with_a_long_random_token
```

Generate a Fernet encryption key in PowerShell:

```powershell
$bytes = New-Object byte[] 32
$rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
$rng.GetBytes($bytes)
[Convert]::ToBase64String($bytes).Replace('+','-').Replace('/','_')
```

For `SETTINGS_ADMIN_TOKEN`, use a long random value you create and keep private. Restart the stack after changing `.env`:

```powershell
docker compose up --build
```

Then open the `...` menu in the app, choose **Admin settings**, and enter that token. Integration values saved there are encrypted in MongoDB and are never returned to the browser.

## Environment variables

| Variable | Required | Purpose |
| --- | --- | --- |
| `GOOGLE_API_KEY` | Yes, for live chat | Gemini API key used by the agent. |
| `SETTINGS_ENCRYPTION_KEY` | Only for Admin settings | Fernet key used to encrypt runtime integration settings. Keep it stable or existing encrypted settings cannot be read. |
| `SETTINGS_ADMIN_TOKEN` | Only for Admin settings | Password used to open the settings screen. |
| `MONGO_URI` | Production only | Connection string for an external MongoDB deployment. Local Compose uses its own MongoDB service. |
| `QDRANT_API_KEY` | External Qdrant only | Leave empty for the included local Qdrant service. It can be entered through Admin settings when using Qdrant Cloud. |

`.env` is deliberately ignored by Git and excluded from Docker build context. Never commit it or put a real key in an issue, screenshot, or chat message.

## Docker data and reset

Docker Compose creates named volumes for MongoDB, Qdrant, and the local SQLite profile database. Your chat history, support requests, runtime settings, and knowledge-base index remain after a normal stop/start.

To remove all local demonstration data, including stored settings and chats:

```powershell
docker compose down -v
```

This command is destructive for this app's local data.

## Publish to Docker Hub

Build from the Dockerfile; do **not** use `docker commit` on a running container.

```powershell
docker login
docker build -t <dockerhub-user>/nile-customer-support-agent:latest .
docker push <dockerhub-user>/nile-customer-support-agent:latest
```

The normal Docker build does not include `.env`: `.dockerignore` excludes it and the Dockerfile does not copy it. Secrets are supplied only when a container starts.

The published `web` image is not a complete standalone installation. It also needs MongoDB and Qdrant. The easiest way for another person to run the full project is to clone this repository, create their own `.env`, and use `docker compose up --build`. If they use only the published image, they must provide reachable MongoDB and Qdrant services plus their own runtime secrets.

## Deploy on Render

`render.yaml` provides a Docker-based Render web-service blueprint.

1. Create a MongoDB Atlas free cluster and database user.
2. Create a Render Web Service from this repository.
3. In Render's environment-variable screen, set `GOOGLE_API_KEY`, `MONGO_URI`, `SETTINGS_ENCRYPTION_KEY`, and `SETTINGS_ADMIN_TOKEN` as secrets.
4. Deploy and check `/healthz`.

The Render free service can sleep when inactive and has temporary disk. MongoDB is therefore used for hosted profile, history, ticket, and encrypted-settings persistence. Free-tier policies can change; check each provider before relying on a deployment.

## Troubleshooting

| Symptom | What to do |
| --- | --- |
| Chat returns `GOOGLE_API_KEY` not configured | Add the key to `.env`, then restart with `docker compose up --build`. |
| Settings screen rejects the token | Confirm `SETTINGS_ADMIN_TOKEN` is in `.env`, then restart the stack. |
| Browser does not show a UI change | Rebuild with `docker compose up --build`, then use `Ctrl+F5`. |
| Need server logs | Run `docker compose logs -f web`. |
| Port 8010 is already used | Stop the conflicting app or change the left-hand port in `docker-compose.yml`. |

## Project structure

```text
app/controllers   HTTP endpoints
app/models        Pydantic request models
app/repositories  SQLite and MongoDB persistence
app/services      LangChain agent, RAG, and runtime settings
frontend/         React chat interface
knowledge_base/   Bundled public-source demonstration content
```

## Verification

```powershell
docker compose up --build
docker compose logs -f web
```
