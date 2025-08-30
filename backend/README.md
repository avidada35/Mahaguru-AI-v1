# Mahaguru AI - Backend

> FastAPI backend for Mahaguru AI, an Agentic AI platform for students.

## 🚀 Features

- **RESTful API** with FastAPI
- **JWT Authentication** with OAuth2
- **PostgreSQL** for relational data
- **Weaviate** for vector search
- **Redis** for caching
- **Document Processing** with AI-powered chunking
- **Async** by default
- **Docker** containerization
- **Alembic** database migrations

## 🛠 Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL + Weaviate
- **Cache**: Redis
- **Auth**: JWT, OAuth2 with Password
- **AI**: LangChain, OpenAI, Sentence Transformers
- **Container**: Docker
- **Testing**: Pytest

## 🏗 Project Structure

```
backend/
├── app/
│   ├── api/               # API routes
│   ├── core/              # Core configurations
│   ├── db/                # Database configurations
│   ├── models/            # SQLAlchemy models
│   └── services/          # Business logic
├── alembic/              # Database migrations
└── tests/                # Test files
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 13+
- Redis
- Weaviate

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -e .[dev]
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

## 📚 API Documentation

- **Interactive API docs**: http://localhost:8000/docs
- **Alternative API docs**: http://localhost:8000/redoc

## 🧪 Testing

```bash
pytest
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

MIT
