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

## AWS deployment (recommended: AWS App Runner + ECR)

You’ll deploy **two containers**:

- `ai-agent-backend` → App Runner service (public URL like `https://xxxx.awsapprunner.com`)
- `ai-agent-frontend` → App Runner service (public URL) that calls the backend URL via `API_URL`

### 1) Create two ECR repositories

In AWS Console:

- ECR → **Create repository** → `ai-agent-backend`
- ECR → **Create repository** → `ai-agent-frontend`

### 2) Build images locally

```bash
docker build -f Dockerfile.backend -t ai-agent-backend .
docker build -f Dockerfile.frontend -t ai-agent-frontend .
```

### 3) Authenticate Docker to ECR

Replace:
- `<region>` e.g. `us-east-1`
- `<account_id>` your AWS account number

```bash
aws ecr get-login-password --region <region> | \
  docker login --username AWS --password-stdin <account_id>.dkr.ecr.<region>.amazonaws.com
```

### 4) Tag and push images to ECR

```bash
docker tag ai-agent-backend:latest <account_id>.dkr.ecr.<region>.amazonaws.com/ai-agent-backend:latest
docker push <account_id>.dkr.ecr.<region>.amazonaws.com/ai-agent-backend:latest

docker tag ai-agent-frontend:latest <account_id>.dkr.ecr.<region>.amazonaws.com/ai-agent-frontend:latest
docker push <account_id>.dkr.ecr.<region>.amazonaws.com/ai-agent-frontend:latest
```

### 5) Create the backend App Runner service

AWS Console:

1. App Runner → **Create service**
2. Source → **Container registry**
3. Provider → **Amazon ECR**
4. Select repo `ai-agent-backend` and image tag `latest`
5. Service settings:
   - **Port**: `9999`
6. Environment variables (set what you use):
   - `GROQ_API_KEY` = `...`
   - `OPENAI_API_KEY` = `...`
   - `TAVILY_API_KEY` = `...` (optional)
7. Create service and wait until it is **Running**

Copy the backend service URL, e.g.:

`https://<backend>.awsapprunner.com`

Your chat endpoint will be:

`https://<backend>.awsapprunner.com/chat`

### 6) Create the frontend App Runner service

AWS Console:

1. App Runner → **Create service**
2. Source → **Container registry** → ECR → repo `ai-agent-frontend`
3. Service settings:
   - **Port**: `8501`
4. Environment variables:
   - `API_URL` = `https://<backend>.awsapprunner.com/chat`
5. Create service → wait for **Running**

Open the frontend App Runner URL in your browser.

## Notes / Tips

- **Don’t commit `.env`**. Commit `.env.example` only.
- If OpenAI requests fail with `429 insufficient_quota`, that’s an account billing/quota issue; Groq may still work.
- For production, consider setting App Runner **instance size** higher if responses are slow.

