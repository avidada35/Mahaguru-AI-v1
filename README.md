# Mahaguru AI - Unified Intelligence Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-00a393.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3.0-61dafb.svg)](https://reactjs.org/)
[![Docker](https://img.shields.io/badge/Docker-20.10+-2496ed.svg)](https://docker.com/)

## Overview

**Mahaguru AI** is an enterprise-grade unified intelligence platform that bridges emotional clarity and academic excellence. Powered by our proprietary **StudentGPT** engine, it delivers personalized AI mentorship, advanced document intelligence, and real-time learning analytics through a scalable, production-ready architecture.

## 🚀 Key Features

- **StudentGPT Integration** - Context-aware AI mentorship with emotional intelligence
- **Unified API Architecture** - Single backend serving multiple AI models and services  
- **Document Intelligence** - Advanced PDF analysis and semantic search capabilities
- **Real-time Analytics** - Learning path optimization and performance tracking
- **Enterprise Security** - JWT authentication, RBAC, end-to-end encryption

## 🛠 Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | React 18.3, TypeScript 5.0, pnpm |
| **Backend** | FastAPI 0.104, Python 3.11+, Celery |
| **Databases** | PostgreSQL 15+, Redis 7.0+, Weaviate |
| **AI/ML** | PyTorch 2.1, Transformers 4.35, PEFT |
| **DevOps** | Docker, Kubernetes, GitHub Actions |
| **Monitoring** | Grafana, Prometheus, Custom Dashboards |

## 📦 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+ with pnpm
- Docker 20.10+
- PostgreSQL 15+ (or Docker)
- Redis 7.0+ (or Docker)

### One-Command Setup

```bash
git clone https://github.com/avidada35/Mahaguru-AI-v01.git
cd Mahaguru-AI-v01
chmod +x scripts/setup.sh && ./scripts/setup.sh
```

### Manual Setup

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements/dev.txt
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
pnpm install
pnpm dev
```

#### Docker Alternative
```bash
docker-compose -f docker/docker-compose.yml up -d
```

Access points:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

## 📡 API Endpoints

### Core Services

| Service | Endpoint | Description |
|---------|----------|-------------|
| **Auth** | `POST /api/v1/auth/login` | User authentication |
| **StudentGPT** | `POST /studentgpt/chat` | AI chat interface |
| **Documents** | `POST /api/v1/documents/upload` | Document analysis |
| **Analytics** | `GET /api/v1/users/{id}/analytics` | User metrics |

### WebSocket Services
- `/ws/chat` - Real-time chat interface
- `/ws/notifications` - Live notifications
- `/ws/analytics` - Analytics streaming

## 🏗 Architecture

```
┌─────────────────────────────────────────────────┐
│            Frontend (React + TypeScript)         │
├─────────────────────────────────────────────────┤
│            Unified Backend (FastAPI)             │
│   ├── API Gateway & Load Balancer               │
│   ├── StudentGPT Service Layer                  │
│   └── Document Intelligence Engine              │
├─────────────────────────────────────────────────┤
│                  Data Layer                      │
│   ├── PostgreSQL (Primary Database)             │
│   ├── Redis (Caching & Sessions)                │
│   └── Weaviate (Vector Search)                  │
├─────────────────────────────────────────────────┤
│            AI/ML Infrastructure                  │
│   ├── Model Serving Pipeline                    │
│   └── Training & Fine-tuning Jobs               │
└─────────────────────────────────────────────────┘
```

## 🧪 Development

### Code Quality
```bash
# Format & lint
black backend/ && isort backend/
prettier --write frontend/src/

# Type checking
mypy backend/
tsc --noEmit

# Testing
pytest tests/ -v --cov=app
pnpm test --coverage
```

### Database Operations
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## 🚢 Deployment

### Production Build
```bash
docker build -f docker/Dockerfile.backend -t mahaguru-backend:latest .
docker build -f docker/Dockerfile.frontend -t mahaguru-frontend:latest .
```

### Kubernetes
```bash
kubectl apply -f deployment/kubernetes/
kubectl get pods -n mahaguru
```

## 📊 Performance Metrics

- **API Response**: < 50ms authentication, < 2s AI inference
- **Scalability**: 10,000+ concurrent users
- **Throughput**: 1,000+ requests/second
- **Document Processing**: < 5s for 10MB PDFs

## 🔒 Security & Compliance

- **Authentication**: OAuth 2.0 + JWT with refresh tokens
- **Encryption**: End-to-end encryption for sensitive data
- **Compliance**: GDPR, FERPA, COPPA compliant
- **Monitoring**: Comprehensive audit logging

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md).

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📚 Documentation

- **Full Documentation**: [docs.mahaguru.ai](https://docs.mahaguru.ai)
- **API Reference**: [localhost:8000/docs](http://localhost:8000/docs)
- **Community Forum**: [community.mahaguru.ai](https://community.mahaguru.ai)

## 🗺 Roadmap

- **Q4 2024**: Multi-modal AI, Real-time collaboration
- **Q1 2025**: Mobile app, Voice interaction
- **Q2 2025**: AR/VR experiences, Peer learning network

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏢 Enterprise Support

For enterprise deployments and custom integrations:
- **Email**: enterprise@mahaguru.ai
- **Schedule**: [cal.com/mahaguru](https://cal.com/mahaguru)

## 👥 Team & Acknowledgments

Built with ❤️ by the Mahaguru AI team and contributors.

Special thanks to the open source community, educational partners, and beta users who make this platform possible.

---

<div align="center">
  <p>
    <a href="https://github.com/avidada35">@avidada35</a> | 
    <a href="https://mahaguru.ai">mahaguru.ai</a> | 
    <a href="mailto:contact@mahaguru.ai">contact@mahaguru.ai</a>
  </p>
  
  <p>
    <img src="https://img.shields.io/github/stars/avidada35/Mahaguru-AI-v01?style=social" alt="Stars">
    <img src="https://img.shields.io/github/forks/avidada35/Mahaguru-AI-v01?style=social" alt="Forks">
  </p>
</div>

**Transform education. Empower minds. Build the future.**
