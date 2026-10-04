# AI-Chatbot-Agents
# Telecom AI Sales Agent

A conversational AI sales-agent prototype for telecom/business communication services.

## What this prototype does

- Website chat interface using Streamlit
- Conversational sales behavior using Groq's OpenAI-compatible API
- Product-aware responses for:
  - Bulk SMS
  - RCS SMS
  - WhatsApp
  - Voice OBD/IBD
  - IVR
  - Toll-Free
- Prospect qualification
- Prospect capture in PostgreSQL
- Simple sales dashboard
- Product-information downloads
- WhatsApp-ready adapter using the same conversation engine


## Run locally

Activate the virtual environment:

```powershell
.venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create `.env`:

```text
GROQ_API_KEY=your_key_here
DB_HOST=localhost
DB_NAME=ai_chatbot
DB_USER=postgres
DB_PASSWORD=your_password
DB_PORT=5432
```

Run:

```powershell
streamlit run app.py
```

## Streamlit Cloud

Add the same values under:

Settings → Secrets

Do not commit `.env`.

## Architecture

```text
Website
   |
   v
Streamlit
   |
   v
Sales Agent
   |
   +---- Product Catalog
   |
   +---- Groq LLM
   |
   +---- Prospect State
   |
   v
PostgreSQL
   |
   v
Sales Dashboard

WhatsApp
   |
   v
Future WhatsApp API adapter
   |
   v
Same Sales Agent
```

The important design choice is that Website and WhatsApp are channels, while the Sales Agent is the shared conversational brain.

## Scope

Current scope is telecom sales only.

