# Self-Hosting DocGenie

DocGenie can be self-hosted using Docker. This guide walks you through deploying DocGenie on your own infrastructure.

---

## Prerequisites

- Docker installed on your machine or server
- Basic familiarity with Docker and Docker Compose

---

## Quick Start

### 1. Get API Keys

You'll need API keys from two services:

**Cohere API Key** (required for embeddings)

- Go to: https://dashboard.cohere.com/api-keys
- Create a free account and generate an API key

**Google AI Studio API Key** (required for LLM)

- Go to: https://aistudio.google.com/app/api-keys
- Create a free account and generate an API key

### 2. Create Configuration File

Copy example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
COHERE_API_KEY=your_cohere_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

### 3. Run with Docker

```bash
docker run -d \
  --name docgenie \
  -p 8000:8000 \
  -v $(pwd)/data:/app/chroma_db \
  --env-file .env \
  docgenie/docgenie:latest
```

### 4. Test Deployment

```bash
curl http://localhost:8000/health
```

You should see: `{"status":"healthy"}`

---

## Using Docker Compose (Recommended)

Docker Compose provides an easier way to manage deployment with automatic volume management.

```bash
# Start service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop service
docker-compose down
```

---

## First Steps

### Generate an API Key

```bash
curl -X POST http://localhost:8000/api/v1/generate
```

Response:

```json
{
  "api_key": "docg_abc123...",
  "created_at": "2024-01-01T00:00:00"
}
```

Save this API key - you'll need it for all API calls.

### Upload a Document

```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -H "X-API-Key: YOUR_API_KEY" \
  -F "file=@/path/to/your/document.pdf"
```

### Query Chatbot

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is in my document?"}'
```

---

## Data Persistence

ChromaDB data is persisted in a Docker volume:

- **Docker Run**: Mounted at `./data` (or your specified path)
- **Docker Compose**: Stored in the `chroma_data` volume

**Backup your data:**

```bash
# Docker Run
tar -czf chroma_backup.tar.gz ./data

# Docker Compose
docker run --rm -v chroma_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/chroma_backup.tar.gz -C /data .
```

---

## Configuration

All configuration is done through environment variables. See `.env.example` for all available options:

| Variable             | Description                          | Default |
| -------------------- | ------------------------------------ | ------- |
| `COHERE_API_KEY`     | Cohere API key (required)            | -       |
| `GOOGLE_API_KEY`     | Google AI API key (required)         | -       |
| `OPENROUTER_API_KEY` | OpenRouter API key (optional)        | -       |
| `CHUNK_SIZE`         | Maximum characters per chunk         | 512     |
| `CHUNK_OVERLAP`      | Characters of overlap between chunks | 50      |
| `DEFAULT_K`          | Number of documents to retrieve      | 6       |

---

## Troubleshooting

### API Key Errors

If you see errors about missing API keys:

- Ensure both `COHERE_API_KEY` and `GOOGLE_API_KEY` are set
- Check that your API keys are valid and have sufficient credits

### Container Won't Start

Check logs for errors:

```bash
docker logs docgenie
# or
docker-compose logs
```

### Data Not Persisting

Ensure you have a volume mounted for ChromaDB:

- Docker: `-v $(pwd)/data:/app/chroma_db`
- Docker Compose: Uses `chroma_data` volume automatically

---

## Next Steps

- Integrate with your application using the REST API
- Check out the API documentation at `http://localhost:8000/docs`
- Explore more configuration options in `.env.example`

---

## Support

For issues or questions:

- Check the [GitHub Issues](https://github.com/yourusername/docgenie/issues)
- Review the [API Documentation](http://localhost:8000/docs)
