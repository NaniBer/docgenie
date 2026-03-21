# DocGenie - Turnkey AI Chatbot Service

A turnkey AI-powered chatbot solution that allows SaaS founders to easily add intelligent document Q&A capabilities to their applications.

## 🎯 What is DocGenie?

DocGenie provides a complete RAG (Retrieval-Augmented Generation) pipeline as a service. Your customers upload documents, and we handle everything - from processing and vectorization to intelligent chatbot responses.

## ✨ Key Features

- **Turnkey Solution**: Ready-made chat module, no setup required
- **Easy Integration**: React component you can drop into your UI
- **Multi-Tenancy**: Isolated vector database collections per customer
- **Multiple Document Formats**: Support for PDF, TXT, MD, DOCX
- **REST API**: Simple, well-documented API endpoints
- **Free AI Models**: Google AI Studio and OpenRouter integration

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/yourusername/docgenie.git
cd docgenie
pip install -r requirements.txt
```

### Configuration

```bash
cp .env.example .env
# Edit .env with your API keys
```

### Run the Server

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## 📚 Documentation

For detailed documentation, see [plan.md](plan.md)

## 🔧 Tech Stack

- **Backend**: Python, FastAPI
- **Vector Database**: ChromaDB
- **Embeddings**: Sentence-Transformers
- **AI Models**: Google AI Studio / OpenRouter
- **Frontend**: React, TypeScript, Tailwind CSS

## 📝 License

MIT

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For questions or support, please open an issue on GitHub.
