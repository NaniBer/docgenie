# DocGenie — Self-hosted RAG Chatbot

Upload documents, ask questions. A complete RAG pipeline you can run anywhere.

---

## How it Works

1. **Upload** any document (PDF, TXT, MD) → split into chunks → embed with Cohere → store in ChromaDB
2. **Query** with natural language → embed your question → find the most relevant chunks → send to an LLM → get an answer with source attribution

Everything runs via API calls to free-tier AI services — no GPU, no heavy models on your machine.

---

## Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/NaniBer/docgenie.git
cd docgenie
cp .env.example .env
# Edit .env with your API keys
```

### 2. Get Your API Keys

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

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

The server starts at `http://localhost:8000`.

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
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL (self-hosted mode) |
| `OLLAMA_MODEL` | `llama3.2` | Ollama model name (self-hosted mode) |

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
