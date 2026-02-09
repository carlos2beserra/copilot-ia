# 🤖 Copilot-IA

> **Intelligent Development Copilots** - A multi-agent AI platform to assist developers throughout the entire software development lifecycle.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Agno](https://img.shields.io/badge/Framework-Agno-purple.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## 📋 Overview

**Copilot-IA** is an AI agent platform built with the **Agno** framework, designed to assist developers with various tasks in the software development cycle. The platform uses a multi-agent system where each copilot specializes in a specific area.

### 🎯 Available Copilots

| Copilot | Description |
|---------|-------------|
| 🔍 **Code Reviewer** | Analyzes code, identifies issues, and suggests improvements |
| 📝 **Documentation** | Generates documentation, docstrings, and README files |
| 🧪 **Testing** | Creates unit, integration, and E2E tests |
| 🐛 **Debug** | Assists in identifying and resolving bugs |
| 🔧 **Refactoring** | Suggests and applies code refactoring |
| 🏗️ **Architecture** | Guides architectural decisions and design patterns |
| 🔒 **Security** | Analyzes vulnerabilities and security best practices |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- API Key from an LLM provider (OpenAI, Anthropic, Groq)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/copilot-ia.git
cd copilot-ia

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit the .env file with your API keys
```

### Basic Usage

```python
from src.copilots import CodeReviewerCopilot

# Initialize the copilot
reviewer = CodeReviewerCopilot()

# Analyze a file
result = reviewer.analyze("path/to/file.py")
print(result)
```

### CLI

```bash
# Review code
copilot review src/main.py

# Generate documentation
copilot docs src/utils/

# Create tests
copilot test src/services/api.py

# Security analysis
copilot security src/
```

---

## 📁 Project Structure

```
copilot-ia/
├── config/                    # YAML configurations
│   ├── agents_config.yaml     # Agent configuration
│   ├── prompts_config.yaml    # Prompt templates
│   └── logging_config.yaml    # Logging configuration
├── src/
│   ├── copilots/              # Specialized copilots
│   │   ├── code_reviewer.py   # Code reviewer
│   │   ├── documentation.py   # Documentation generator
│   │   ├── testing.py         # Test generator
│   │   ├── debug.py           # Debug assistant
│   │   ├── refactoring.py     # Refactoring expert
│   │   ├── architecture.py    # Architecture advisor
│   │   └── security.py        # Security analyzer
│   ├── agents/                # Base Agno agents
│   │   ├── base.py            # Abstract base agent
│   │   └── coordinator.py     # Multi-agent coordinator
│   ├── tools/                 # Agent tools
│   │   ├── code_analysis.py   # Code analysis
│   │   ├── file_operations.py # File operations
│   │   ├── git_tools.py       # Git tools
│   │   └── search_tools.py    # Search tools
│   ├── utils/                 # Utilities
│   │   ├── code_parser.py     # Code parser
│   │   ├── token_counter.py   # Token counter
│   │   └── cache.py           # Cache system
│   └── api/                   # REST API
│       ├── main.py            # FastAPI application
│       └── routes/            # API routes
├── examples/                  # Usage examples
├── notebooks/                 # Jupyter notebooks
├── tests/                     # Automated tests
├── Dockerfile                 # Docker container
├── docker-compose.yml         # Container orchestration
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# LLM Provider (choose one)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GROQ_API_KEY=gsk_...

# Default model
DEFAULT_MODEL=gpt-4o
DEFAULT_PROVIDER=openai

# Cache
CACHE_ENABLED=true
CACHE_TTL=3600

# Logging
LOG_LEVEL=INFO
```

### Agent Configuration

Edit `config/agents_config.yaml` to customize the agents:

```yaml
agents:
  code_reviewer:
    model: gpt-4o
    temperature: 0.3
    max_tokens: 4096
    tools:
      - code_analysis
      - file_operations
```

---

## 🔧 Development

### Run Tests

```bash
pytest tests/ -v --cov=src
```

### Linting and Formatting

```bash
ruff check src/
black src/
mypy src/
```

### Run API Locally

```bash
uvicorn src.api.main:app --reload --port 8000
```

---

## 🐳 Docker

```bash
# Build image
docker build -t copilot-ia .

# Run container
docker run -p 8000:8000 --env-file .env copilot-ia

# Or with docker-compose
docker-compose up -d
```

### Quick Commands

```bash
make up       # Start containers
make down     # Stop containers
make logs     # View logs
make restart  # Restart containers
```

---

## 🌐 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/review` | POST | Code review |
| `/api/v1/docs` | POST | Generate documentation |
| `/api/v1/test` | POST | Generate tests |
| `/api/v1/security` | POST | Security analysis |
| `/api/v1/debug` | POST | Debug assistance |

### Example Request

```bash
curl -X POST http://localhost:8000/api/v1/review \
  -H "Content-Type: application/json" \
  -d '{"code": "def foo(): pass", "language": "python"}'
```

---

## 🌍 Supported Languages

| Language | Full Support | Code Review | Tests |
|----------|--------------|-------------|-------|
| Python | ✅ | ✅ | pytest, unittest |
| JavaScript | ⚠️ | ✅ | jest, vitest |
| TypeScript | ⚠️ | ✅ | jest, vitest |
| Java | ⚠️ | ✅ | JUnit |
| Go | ⚠️ | ✅ | go test |
| Rust | ⚠️ | ✅ | cargo test |

---

## 📚 Additional Documentation

- [Quick Start Guide](docs/QUICKSTART.md)
- [Deployment Guide](docs/DEPLOY_GUIDE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [API Reference](docs/API.md)

---

## 🤝 Contributing

Contributions are welcome! Please read the [contribution guide](docs/CONTRIBUTING.md) before submitting PRs.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Agno Framework](https://github.com/agno-agi/agno) - AI agents framework
- [OpenAI](https://openai.com) - Language models
- [Anthropic](https://anthropic.com) - Claude AI

---

**Made with ❤️ for developers**
