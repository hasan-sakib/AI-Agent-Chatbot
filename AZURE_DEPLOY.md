# Deploying to Azure Container Apps with Supabase

This guide walks you through deploying the AI Agent Chatbot to **Azure Container Apps** (free tier) using **Supabase** (free hosted PostgreSQL) for persistent chat history. No paid services required for a student account.

---

## Prerequisites

| Tool | Install |
|---|---|
| Azure CLI | https://learn.microsoft.com/en-us/cli/azure/install-azure-cli |
| Docker Desktop | https://www.docker.com/products/docker-desktop |
| Azure Student account | https://azure.microsoft.com/en-us/free/students |
| Supabase account | https://supabase.com (free, no credit card needed) |

Log in to Azure before starting:
```bash
az login
```

---

## Step 1 — Set Up Supabase (Free PostgreSQL)

1. Go to [supabase.com](https://supabase.com) and click **Start your project**
2. Create a new organisation and a new project (choose any region close to your Azure region)
3. Set a strong database password and save it — you will need it shortly
4. Wait ~2 minutes for the project to be provisioned

### Get your connection string

1. In your Supabase project, go to **Settings → Database**
2. Scroll to **Connection string** and select the **URI** tab
3. Copy the string — it looks like:
   ```
   postgresql://postgres:<password>@db.<project-ref>.supabase.co:5432/postgres
   ```
4. Replace `<password>` with the password you set in step 3

> **Note:** The app's `db.py` automatically creates the required tables (`chat_sessions`, `chat_messages`) on first startup — you don't need to run any SQL manually.

---

## Step 2 — Define Shell Variables

Set these once in your terminal. Every command below uses them.

```bash
export RG=ai-agent-rg
export LOCATION=eastus                   # change to a region near you
export ACR_NAME=aiagentregistry          # must be globally unique — change if taken
export ENV_NAME=ai-agent-env
export BACKEND_APP=ai-agent-backend
export FRONTEND_APP=ai-agent-frontend

# Paste your Supabase connection string here:
export DATABASE_URL="postgresql://postgres:<password>@db.<project-ref>.supabase.co:5432/postgres"

# Your LLM / search API keys:
export GROQ_API_KEY="your-groq-key"
export OPENAI_API_KEY="your-openai-key"
export TAVILY_API_KEY="your-tavily-key"
```

---

## Step 3 — Create Azure Resources

```bash
# Resource group
az group create --name $RG --location $LOCATION

# Azure Container Registry (stores your Docker images)
az acr create \
  --resource-group $RG \
  --name $ACR_NAME \
  --sku Basic \
  --admin-enabled true

# Container Apps environment (the shared networking layer)
az containerapp env create \
  --name $ENV_NAME \
  --resource-group $RG \
  --location $LOCATION
```

---

## Step 4 — Build and Push Docker Images

```bash
# Log in to your registry
az acr login --name $ACR_NAME

# Build and push the backend image
docker build -f Dockerfile.backend \
  -t $ACR_NAME.azurecr.io/ai-agent-backend:latest .
docker push $ACR_NAME.azurecr.io/ai-agent-backend:latest

# Build and push the frontend image
docker build -f Dockerfile.frontend \
  -t $ACR_NAME.azurecr.io/ai-agent-frontend:latest .
docker push $ACR_NAME.azurecr.io/ai-agent-frontend:latest
```

---

## Step 5 — Get ACR Credentials

```bash
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query "username" -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)
```

---

## Step 6 — Deploy the Backend

```bash
# Deploy the backend container app
az containerapp create \
  --name $BACKEND_APP \
  --resource-group $RG \
  --environment $ENV_NAME \
  --image $ACR_NAME.azurecr.io/ai-agent-backend:latest \
  --registry-server $ACR_NAME.azurecr.io \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --target-port 9999 \
  --ingress external \
  --min-replicas 0 \
  --max-replicas 2

# Store secrets (API keys + Supabase URL) securely — not as plain env vars
az containerapp secret set \
  --name $BACKEND_APP \
  --resource-group $RG \
  --secrets \
    groq-key="$GROQ_API_KEY" \
    openai-key="$OPENAI_API_KEY" \
    tavily-key="$TAVILY_API_KEY" \
    database-url="$DATABASE_URL"

# Wire the secrets to environment variables
az containerapp update \
  --name $BACKEND_APP \
  --resource-group $RG \
  --set-env-vars \
    GROQ_API_KEY=secretref:groq-key \
    OPENAI_API_KEY=secretref:openai-key \
    TAVILY_API_KEY=secretref:tavily-key \
    DATABASE_URL=secretref:database-url

# Get the backend's public URL
BACKEND_FQDN=$(az containerapp show \
  --name $BACKEND_APP \
  --resource-group $RG \
  --query "properties.configuration.ingress.fqdn" -o tsv)

echo "Backend URL: https://$BACKEND_FQDN"
```

---

## Step 7 — Deploy the Frontend

```bash
az containerapp create \
  --name $FRONTEND_APP \
  --resource-group $RG \
  --environment $ENV_NAME \
  --image $ACR_NAME.azurecr.io/ai-agent-frontend:latest \
  --registry-server $ACR_NAME.azurecr.io \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --target-port 8501 \
  --ingress external \
  --min-replicas 0 \
  --max-replicas 2 \
  --env-vars API_URL="https://$BACKEND_FQDN/chat"

# Get the frontend's public URL
FRONTEND_FQDN=$(az containerapp show \
  --name $FRONTEND_APP \
  --resource-group $RG \
  --query "properties.configuration.ingress.fqdn" -o tsv)

echo "Frontend URL: https://$FRONTEND_FQDN"
```

Open `https://$FRONTEND_FQDN` in your browser — the chatbot is live!

---

## Step 8 — Verify the Deployment

```bash
# Check backend logs (real-time)
az containerapp logs show \
  --name $BACKEND_APP \
  --resource-group $RG \
  --follow

# Test the API docs page
curl https://$BACKEND_FQDN/docs

# Test the history endpoint (should return [])
curl https://$BACKEND_FQDN/history/00000000-0000-0000-0000-000000000000
```

To confirm chat history is being saved:
1. Open the frontend URL and send a few messages
2. Go to your Supabase project → **Table Editor** → `chat_messages`
3. You should see rows with your conversation

---

## Step 9 — Updating After Code Changes

Rebuild and push the changed image, then tell Container Apps to pull it:

```bash
# Example: update the backend after a code change
docker build -f Dockerfile.backend \
  -t $ACR_NAME.azurecr.io/ai-agent-backend:latest .
docker push $ACR_NAME.azurecr.io/ai-agent-backend:latest

az containerapp update \
  --name $BACKEND_APP \
  --resource-group $RG \
  --image $ACR_NAME.azurecr.io/ai-agent-backend:latest

# Same pattern for the frontend
docker build -f Dockerfile.frontend \
  -t $ACR_NAME.azurecr.io/ai-agent-frontend:latest .
docker push $ACR_NAME.azurecr.io/ai-agent-frontend:latest

az containerapp update \
  --name $FRONTEND_APP \
  --resource-group $RG \
  --image $ACR_NAME.azurecr.io/ai-agent-frontend:latest
```

---

## Cost & Free Tier Summary

| Service | Free allowance | Notes |
|---|---|---|
| Azure Container Apps | 180,000 vCPU-s + 360,000 GiB-s / month | `--min-replicas 0` scales to zero when idle |
| Azure Container Registry (Basic) | ~$5/month | Smallest paid SKU — uses Azure student credit |
| Supabase | 500 MB DB, 2 GB bandwidth | Completely free, no credit card |
| Azure Student credit | $100 total | ACR Basic is the only cost (~$5/month → ~20 months of credit) |

> **Tip:** Set `--min-replicas 0` (already in the commands above) so containers scale to zero when not in use. The free grant covers normal personal/demo usage with room to spare.

---

## SSL / Firewall Notes

- Supabase free tier **requires** `sslmode=require` — `db.py` appends it automatically if missing from your connection string.
- Supabase free tier does **not** support IP allowlisting, so no firewall rules are needed. Azure Container Apps outbound IPs are accepted automatically.
- All Container Apps endpoints are HTTPS by default — no extra TLS configuration needed.

---

## Teardown (When You're Done)

This deletes all Azure resources in one command:

```bash
az group delete --name $RG --yes --no-wait
```

To delete the Supabase project: go to **Settings → General → Delete project** in the Supabase dashboard.
