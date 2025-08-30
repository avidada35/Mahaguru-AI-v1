# Mahaguru AI

A modern AI-powered learning platform built with React, FastAPI, and modern tooling.

## 🚀 Features

- **Frontend**: Modern React application with TypeScript, Tailwind CSS, and shadcn/ui
- **Backend**: FastAPI with Python 3.11
- **Database**: PostgreSQL for relational data
- **Vector Database**: Weaviate for semantic search and embeddings
- **Caching**: Redis for performance optimization
- **Containerized**: Docker and Docker Compose for easy development and deployment
- **CI/CD**: GitHub Actions for automated testing and deployment

## 🛠️ Prerequisites

- Node.js 20+
- Python 3.11
- Docker & Docker Compose
- pnpm

## 🚀 Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/mahaguru-ai.git
   cd mahaguru-ai
   ```

2. Install dependencies:
   ```bash
   pnpm install
   cd backend && pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Start the development environment:
   ```bash
   docker-compose up -d
   ```

5. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 🏗 Project Structure

```
.
├── backend/           # FastAPI backend
├── frontend/          # React frontend
├── shared/            # Shared utilities and types
├── .github/           # GitHub Actions workflows
├── docker-compose.yml # Docker Compose configuration
└── package.json       # Root package.json for workspaces
```

## 🧪 Testing

Run tests for all workspaces:
```bash
pnpm test
```

## 🚀 Deployment

Deployment is handled automatically via GitHub Actions on the `main` branch.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
