# LangGraph AI Agent Chatbot (Streamlit + FastAPI)

This repo contains:

- **Frontend**: Streamlit app (`frontend.py`)
- **Backend**: FastAPI API (`backend.py`) that calls the agent (`ai_agent.py`)

## Prerequisites

- Docker + Docker Compose (recommended), or Python 3.11 + Pipenv
- API keys (do **not** commit your `.env`)
  - `GROQ_API_KEY` (for Groq models)
  - `OPENAI_API_KEY` (for OpenAI models)
  - `TAVILY_API_KEY` (only if you enable search)

## Local run (Docker Compose)

1) Export your keys in your terminal (or use a local `.env` file **not committed**):

```bash
export GROQ_API_KEY="..."
export OPENAI_API_KEY="..."
export TAVILY_API_KEY="..."
```

2) Build & run both services:

```bash
docker compose up --build
```

3) Open:

- **Streamlit UI**: `http://localhost:8501`
- **FastAPI docs**: `http://localhost:9999/docs`

### Local run (Docker only, separately)

Backend:

```bash
docker build -f Dockerfile.backend -t ai-agent-backend .
docker run --rm -p 9999:9999 \
  -e GROQ_API_KEY="$GROQ_API_KEY" \
  -e OPENAI_API_KEY="$OPENAI_API_KEY" \
  -e TAVILY_API_KEY="$TAVILY_API_KEY" \
  ai-agent-backend
```

Frontend (point it to the backend):

```bash
docker build -f Dockerfile.frontend -t ai-agent-frontend .
docker run --rm -p 8501:8501 \
  -e API_URL="http://host.docker.internal:9999/chat" \
  ai-agent-frontend
```

## Azure deployment (recommended: Azure Container Apps + ACR)

You’ll deploy **two containers**:

- `ai-agent-backend` → Azure Container App (public URL)
- `ai-agent-frontend` → Azure Container App (public URL) that calls the backend URL via `API_URL`

### 0) Prereqs

- Install and sign in with Azure CLI:

```bash
az login
```

### 1) Create an Azure resource group

Replace `<region>` with a valid Azure region name (example: `eastus`).

```bash
az group create --name ai-agent-rg --location <region>
```

### 2) Create an Azure Container Registry (ACR)

Pick a globally-unique registry name (lowercase, no dashes).

```bash
az acr create --resource-group ai-agent-rg --name <acrName> --sku Basic
az acr login --name <acrName>
```

### 3) Build images locally

```bash
docker build -f Dockerfile.backend -t ai-agent-backend .
docker build -f Dockerfile.frontend -t ai-agent-frontend .
```

### 4) Tag and push images to ACR

Replace:
- `<acrName>` your ACR name

```bash
docker tag ai-agent-backend:latest <acrName>.azurecr.io/ai-agent-backend:latest
docker push <acrName>.azurecr.io/ai-agent-backend:latest

docker tag ai-agent-frontend:latest <acrName>.azurecr.io/ai-agent-frontend:latest
docker push <acrName>.azurecr.io/ai-agent-frontend:latest
```

### 5) Create an Azure Container Apps environment

```bash
az extension add --name containerapp --upgrade
az provider register --namespace Microsoft.App
az provider register --namespace Microsoft.OperationalInsights

az containerapp env create \
  --name ai-agent-env \
  --resource-group ai-agent-rg \
  --location <region>
```

### 6) Deploy the backend container app

This exposes the backend publicly and listens on port `9999`.

```bash
az containerapp create \
  --name ai-agent-backend \
  --resource-group ai-agent-rg \
  --environment ai-agent-env \
  --image <acrName>.azurecr.io/ai-agent-backend:latest \
  --registry-server <acrName>.azurecr.io \
  --target-port 9999 \
  --ingress external \
  --env-vars \
    GROQ_API_KEY="$GROQ_API_KEY" \
    OPENAI_API_KEY="$OPENAI_API_KEY" \
    TAVILY_API_KEY="$TAVILY_API_KEY"
```

Get the backend URL:

```bash
az containerapp show \
  --name ai-agent-backend \
  --resource-group ai-agent-rg \
  --query properties.configuration.ingress.fqdn -o tsv
```

Your chat endpoint will be:

`https://<backend-fqdn>/chat`

### 7) Deploy the frontend container app

Set `API_URL` to your backend endpoint and expose Streamlit on port `8501`.

```bash
az containerapp create \
  --name ai-agent-frontend \
  --resource-group ai-agent-rg \
  --environment ai-agent-env \
  --image <acrName>.azurecr.io/ai-agent-frontend:latest \
  --registry-server <acrName>.azurecr.io \
  --target-port 8501 \
  --ingress external \
  --env-vars \
    API_URL="https://<backend-fqdn>/chat"
```

Get the frontend URL:

```bash
az containerapp show \
  --name ai-agent-frontend \
  --resource-group ai-agent-rg \
  --query properties.configuration.ingress.fqdn -o tsv
```

Open:

`https://<frontend-fqdn>`

## Notes / Tips

- **Don’t commit `.env`**. Commit `.env.example` only.
- If OpenAI requests fail with `429 insufficient_quota`, that’s an account billing/quota issue; Groq may still work.
- For production, consider increasing Container Apps CPU/memory if responses are slow.

