# DocGenie — Self-hosted RAG Chatbot

Upload documents, ask questions. A complete RAG pipeline in one Docker container.

```bash
docker run -d -p 8000:8000 -v $(pwd)/chroma_db:/app/chroma_db --env-file .env docgenie/docgenie
curl -X POST http://localhost:8000/api/v1/upload -F "file=@doc.pdf"
curl -X POST http://localhost:8000/api/v1/query -H "Content-Type: application/json" -d '{"query": "What is this about?"}'
```

---

## How it Works

1. **Upload** any document (PDF, TXT, MD) → split into chunks → embed with Cohere → store in ChromaDB
2. **Query** with natural language → embed your question → find the most relevant chunks → send to an LLM → get an answer with source attribution

Everything runs via API calls to free-tier AI services — no GPU, no heavy models on your machine.

---

## Quick Start

### 1. Get Your API Keys

| Service | Why | Sign Up |
|---|---|---|
| OpenRouter | Powers the chatbot responses | https://openrouter.ai/keys |
| Cohere | Converts text to vectors (embeddings) | https://dashboard.cohere.com/api-keys |
| Google AI | Optional LLM fallback | https://aistudio.google.com/app/apikey |

All three have generous free tiers.

### 2. Configure

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Run

**With Docker** (recommended):
```bash
docker compose up -d
```

**Without Docker:**
```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

The server starts at `http://localhost:8000`.

---

## Deployment

Once running, upload a document and ask questions via the API. No UI, no database — just a single container.

### Option 1: VPS (DigitalOcean, Linode, Hetzner, etc.)

```bash
ssh root@your-vm
# Install Docker if needed
curl -fsSL https://get.docker.com | sh

# Create a .env file with your API keys
cat > .env << EOF
MODE=cloud
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-...
COHERE_API_KEY=...
EOF

# Run the container
docker run -d -p 8000:8000 \
  -v $(pwd)/chroma_db:/app/chroma_db \
  --env-file .env \
  docgenie/docgenie
```

Your API is now live at `http://your-vm-ip:8000`. Add Nginx with SSL for production.

### Option 2: Railway / Render / Fly.io (serverless)

Connect your GitHub repo to any of these platforms:

1. Set build command: (not needed — use Dockerfile)
2. Set start command: (not needed)
3. Add these environment variables:
   - `MODE=cloud`
   - `OPENROUTER_API_KEY=...`
   - `COHERE_API_KEY=...`
4. Deploy

You'll get a public URL like `docgenie.railway.app`.

### Option 3: Docker Compose (anywhere)

```bash
git clone https://github.com/youruser/docgenie.git
cd docgenie
cp .env.example .env
# Edit .env with your API keys
docker compose up -d
```

Works on any machine with Docker installed.

---

All endpoints at `/api/v1/`.

### Upload a document

```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@report.pdf"
```

```json
{"filename": "report.pdf", "chunks_created": 12, "chunks_stored": 12, "file_size": 248102}
```

### Upload multiple documents

```bash
curl -X POST http://localhost:8000/api/v1/upload-multiple \
  -F "files=@doc1.pdf" -F "files=@doc2.txt"
```

### Ask a question

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the main topic?"}'
```

```json
{
  "answer": "The document covers...",
  "sources": [{"content": "...", "metadata": {"source_file": "report.pdf"}, "source": "..."}],
  "query_time_ms": 3452
}
```

### Check stats

```bash
curl http://localhost:8000/api/v1/stats
```

### Clear all documents

```bash
curl -X DELETE http://localhost:8000/api/v1/clear
```

---

## Configuration

All options in `.env`:

| Variable | Default | Description |
|---|---|---|
| `MODE` | `cloud` | `cloud` or `self-hosted` (for Ollama) |
| `LLM_PROVIDER` | `openrouter` | `openrouter` or `google` |
| `OPENROUTER_API_KEY` | — | Your OpenRouter key |
| `OPENROUTER_MODEL` | `openrouter/free` | Model to use for chat |
| `COHERE_API_KEY` | — | Your Cohere key (embeddings) |
| `GOOGLE_API_KEY` | — | Your Google AI key (fallback LLM) |
| `CHROMA_PERSIST_DIRECTORY` | `./chroma_db` | Where vectors are stored |
| `COLLECTION_NAME` | `documents` | ChromaDB collection name |
| `CHUNK_SIZE` | `500` | Max characters per chunk |
| `CHUNK_OVERLAP` | `50` | Overlap between chunks |
| `DEFAULT_K` | `6` | Number of chunks to retrieve per query |

---

## Self-hosted Mode (Ollama)

If you want everything local with zero API calls:

1. Install [Ollama](https://ollama.com) and pull a model: `ollama pull llama3.2`
2. Set `MODE=self-hosted` in `.env`
3. Start the server

The server will use Ollama for the LLM and local HuggingFace embeddings (on CPU). No API keys needed, but embedding is slower.

---

## Tech Stack

- **Backend**: Python, FastAPI
- **Vector DB**: ChromaDB (persistent, file-based)
- **Embeddings**: Cohere (cloud) or HuggingFace (self-hosted)
- **LLM**: OpenRouter, Google Gemini, or Ollama
- **Docs**: PDF, TXT, MD (via LangChain loaders)

---

## License

MIT
