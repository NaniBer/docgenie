# DocGenie - Turnkey AI Chatbot Service

## Overview
A turnkey AI-powered chatbot solution that allows SaaS founders to easily add intelligent document Q&A capabilities to their applications. Customers upload documents, and we handle the entire RAG (Retrieval-Augmented Generation) pipeline.

## Value Proposition

### For Founders/SaaS Customers
- **Turnkey Solution**: Ready-made chat module, no setup required
- **Easy Integration**: React component they can drop into their UI
- **Admin Panel**: Upload docs, manage settings, view logs without code
- **Premium Feature**: Offer custom AI-powered help centers to their users
- **Competitive Advantage**: "Our platform comes with an AI assistant"

### For End Users
- **Instant Answers**: Get contextual responses about content, docs, FAQs
- **Improved Engagement**: Better user satisfaction and retention
- **Smart Sidekick**: AI assistant always available

## Architecture

### System Architecture
```
Customer Website/App (React/Next.js)
    ↓
DocGenie React Chatbot Component
    ↓
DocGenie FastAPI Backend (REST API)
    ↓
├── Document Processing Pipeline
│   ├── Document Upload
│   ├── Text Extraction
│   ├── Chunking
│   └── Embedding
├── Vector Database (ChromaDB)
│   └── Isolated Collections per Customer
└── AI Model Integration
    ├── Query Embedding
    ├── Vector Search
    └── Response Generation (Google AI/OpenRouter)
```

### Tech Stack

**Backend (Python)**
- **Framework**: FastAPI
- **Vector Database**: ChromaDB (multi-tenant with isolated collections)
- **Embeddings**: Sentence-Transformers (all-MiniLM-L6-v2)
- **Document Processing**: pypdf for PDFs, python-docx for docs, markdown support
- **AI Models**: Google AI Studio API or OpenRouter API

**Frontend (React/TypeScript)**
- **UI Component**: React chatbot widget
- **Styling**: Tailwind CSS (compatible with shadcn/ui)
- **Type-safe**: TypeScript definitions

## Features

### Core Features
1. **Document Upload API**
   - Single document upload
   - Batch upload support
   - Multiple file formats (PDF, TXT, MD, DOCX)
   - Automatic processing and vectorization

2. **Chat Query API**
   - Natural language queries
   - Context-aware responses
   - Source attribution
   - Streaming responses (optional)

3. **Multi-Tenancy**
   - Isolated vector database collections per customer
   - API key-based authentication
   - Per-customer document management

4. **React Chatbot Component**
   - Drop-in integration
   - Customizable appearance
   - TypeScript support
   - Responsive design

### Advanced Features (Future)
1. **Admin Dashboard**
   - Document management UI
   - Chat logs and analytics
   - Settings configuration

2. **Monitoring & Analytics**
   - Query analytics
   - Response times
   - Popular topics
   - User engagement metrics

3. **Advanced Chunking**
   - Semantic chunking
   - Smart overlap
   - Custom chunk sizes

4. **Streaming Responses**
   - Real-time answer generation
   - Better user experience

## API Design

### Endpoints

**Document Management**
- `POST /api/v1/documents/upload` - Upload single document
- `POST /api/v1/documents/upload-multiple` - Upload multiple documents
- `DELETE /api/v1/documents/clear` - Clear all documents for customer

**Chat**
- `POST /api/v1/chat/query` - Query the chatbot

**Health/Status**
- `GET /` - API info
- `GET /health` - Health check

### Request/Response Examples

**Upload Document**
```json
// POST /api/v1/documents/upload
// Content-Type: multipart/form-data
// Body: file + api_key (header)
Response: {
  "message": "Document processed successfully",
  "filename": "document.pdf",
  "customer_id": "customer123"
}
```

**Query Chatbot**
```json
// POST /api/v1/chat/query
{
  "query": "What is the refund policy?",
  "api_key": "customer123"
}
Response: {
  "answer": "Our refund policy allows...",
  "sources": ["document.pdf:page5", "document.pdf:page12"]
}
```

## Project Structure

```
DocGenie/
├── main.py                 # FastAPI application entry point
├── config.py               # Configuration and settings
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── plan.md                # This file
│
├── routers/
│   ├── documents.py       # Document upload endpoints
│   └── chat.py            # Chat query endpoints
│
├── services/
│   ├── document_processor.py  # Document processing pipeline
│   ├── vector_store.py        # ChromaDB management
│   ├── embedding_service.py   # Embedding generation
│   └── chat_service.py        # Chat logic and AI integration
│
├── models/
│   ├── schemas.py         # Pydantic models
│   └── database.py        # Database models (if needed)
│
├── chatbot-component/     # React chatbot widget
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── types/
│   │   └── index.tsx
│   ├── package.json
│   └── README.md
│
├── chroma_db/            # Vector database storage (auto-created)
├── uploads/              # Temporary file storage (auto-created)
│
├── tests/                # Test files
├── docs/                 # Documentation
└── README.md             # Main documentation
```

## Implementation Phases

### Phase 1: MVP Core Backend (Week 1)
- [ ] Set up FastAPI project structure
- [ ] Configure ChromaDB with multi-tenancy
- [ ] Implement document upload endpoint
- [ ] Implement basic chunking strategy
- [ ] Implement embedding generation
- [ ] Implement vector storage
- [ ] Implement basic query endpoint
- [ ] Connect to AI model (Google AI or OpenRouter)
- [ ] Test with sample documents

### Phase 2: Enhanced Backend (Week 2)
- [ ] Improve chunking strategy
- [ ] Add source attribution
- [ ] Implement batch document upload
- [ ] Add error handling and validation
- [ ] Add API key authentication
- [ ] Add document management (clear/delete)
- [ ] Performance optimization
- [ ] Add logging and monitoring basics

### Phase 3: React Chatbot Component (Week 3)
- [ ] Create React component structure
- [ ] Implement chat UI
- [ ] Add message history
- [ ] Integrate with API
- [ ] Add TypeScript definitions
- [ ] Style with Tailwind CSS
- [ ] Make responsive
- [ ] Add loading states
- [ ] Add error handling

### Phase 4: Documentation & Testing (Week 4)
- [ ] Write comprehensive README
- [ ] Create API documentation
- [ ] Write integration tests
- [ ] Write unit tests
- [ ] Create example usage
- [ ] Document deployment process

### Phase 5: Advanced Features (Future)
- [ ] Admin dashboard
- [ ] Analytics and monitoring
- [ ] Streaming responses
- [ ] Advanced chunking strategies
- [ ] Multiple AI model support
- [ ] Rate limiting
- [ ] Caching layer

## Deployment Options

### Development
- Local development with uvicorn
- Local ChromaDB instance
- Environment variables in .env

### Production Options
**Option 1: Self-Hosted (Recommended for MVP)**
- Docker container
- Cloud server (AWS EC2, DigitalOcean, etc.)
- Managed database for ChromaDB (or persistent volume)
- Nginx as reverse proxy

**Option 2: Cloud Services**
- AWS ECS/Fargate
- Google Cloud Run
- Azure App Service
- Managed vector databases (Pinecone, etc.)

## Security Considerations

- API key authentication
- Input validation and sanitization
- File type validation
- Size limits on uploads
- Rate limiting (future)
- Secure environment variable management
- HTTPS only in production

## Configuration

### Environment Variables
```env
API_KEY=your_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHUNK_SIZE=512
CHUNK_OVERLAP=50
```

## Usage Examples

### For Developers (Python)
```python
# Install
pip install docgenie

# Upload documents
from docgenie import DocGenieClient
client = DocGenieClient(api_key="your_api_key")
client.upload_document("path/to/document.pdf")

# Query
response = client.query("What is the refund policy?")
print(response.answer)
```

### For Developers (React)
```tsx
import { DocGenieChatbot } from '@docgenie/react-chatbot';

function App() {
  return (
    <DocGenieChatbot
      apiKey="your_api_key"
      theme="dark"
      position="bottom-right"
    />
  );
}
```

### REST API
```bash
# Upload document
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -H "X-API-Key: your_api_key" \
  -F "file=@document.pdf"

# Query
curl -X POST http://localhost:8000/api/v1/chat/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the refund policy?", "api_key": "your_api_key"}'
```

## Next Steps

1. **Initialize Project**
   - Set up git repository
   - Create project structure
   - Install dependencies

2. **Core Development**
   - Implement FastAPI backend
   - Set up ChromaDB
   - Create document processing pipeline
   - Build query functionality

3. **Frontend Component**
   - Create React chatbot widget
   - Integrate with API
   - Style and polish

4. **Testing & Documentation**
   - Test thoroughly
   - Write documentation
   - Create examples

5. **Launch**
   - Deploy to production
   - Monitor performance
   - Gather feedback
   - Iterate and improve

## Questions & Decisions Needed

- [ ] Finalize AI model provider (Google AI vs OpenRouter)
- [ ] Decide on authentication mechanism (API keys vs OAuth)
- [ ] Determine deployment strategy
- [ ] Define pricing model (free tier, pricing tiers)
- [ ] Plan monitoring and analytics approach
- [ ] Decide on customer support strategy

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Sentence-Transformers](https://www.sbert.net/)
- [Google AI Studio](https://ai.google.dev/)
- [OpenRouter](https://openrouter.ai/)
