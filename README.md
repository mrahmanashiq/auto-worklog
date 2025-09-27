# 🚀 Worklog Automation System

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Tested with pytest](https://img.shields.io/badge/tested%20with-pytest-blue.svg)](https://docs.pytest.org/en/latest/)

An AI-friendly, modern worklog management and automation system built with FastAPI, designed for seamless integration with Teams, Jira, and other productivity tools.

## ✨ Features

- **⏰ Smart Time Tracking**: Automatic work day management starting from 8:00 AM
- **🎯 One-Click Meeting Timer**: Effortless meeting time tracking
- **📊 Intelligent Reports**: Auto-generated daily/weekly summaries
- **🔗 Multi-Platform Export**: Teams, Jira, TXT, CSV, PDF outputs
- **🤖 AI-Friendly Architecture**: Clean, documented code perfect for AI assistance
- **⚡ Real-time Updates**: WebSocket support for live tracking
- **🔐 Secure**: OAuth2 + JWT authentication
- **📈 Analytics**: Productivity insights and time distribution

## 🛠️ Tech Stack

- **Backend**: FastAPI 0.104+ with Python 3.11+
- **Database**: SQLModel (SQLAlchemy 2.0) with PostgreSQL/SQLite
- **Cache/Queue**: Redis + Celery for background tasks
- **Auth**: OAuth2 + JWT with proper security
- **Monitoring**: Loguru + Prometheus + Sentry
- **Testing**: Pytest with 100% async support
- **Code Quality**: Ruff (linting/formatting) + MyPy (type checking)

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL (optional, SQLite is used by default for development)
- Redis (optional, for background tasks)

## 📦 Installation

Choose your preferred installation method:

## 🐳 Option 1: Using Docker (Recommended for Production)

### 1. Using Docker Compose (Full Stack)

```bash
# Clone the repository
git clone https://github.com/mrahmanashiq/auto-worklog.git
cd auto-worklog

# Start all services (FastAPI + PostgreSQL + Redis + Celery)
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

### 2. Using Docker for App Only

```bash
# Build the image
docker build -t worklog-automation .

# Run with SQLite (development)
docker run -p 8000:8000 \
  -e DATABASE_URL="sqlite+aiosqlite:///./worklog.db" \
  worklog-automation

# Run with external PostgreSQL
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/db" \
  -e REDIS_URL="redis://redis-host:6379/0" \
  worklog-automation
```

## 🐍 Option 2: Using Python Virtual Environment (Recommended for Development)

### 1. Setup Virtual Environment

```bash
# Clone the repository
git clone https://github.com/mrahmanashiq/auto-worklog.git
cd auto-worklog

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (Git Bash/PowerShell):
source venv/Scripts/activate
# On Windows (Command Prompt):
venv\Scripts\activate.bat
# On macOS/Linux:
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt -r requirements-dev.txt
```

### 2. Environment Configuration

```bash
# Copy environment template (if exists) or use the default .env
cp .env.example .env  # if available

# Edit configuration (optional, defaults work for development)
nano .env  # or use your favorite editor
```

The `.env` file contains development-friendly defaults:
- SQLite database (no setup required)
- Debug mode enabled
- All external integrations disabled

### 3. Run the Application

```bash
# Make sure your virtual environment is activated
source venv/Scripts/activate  # Windows Git Bash
# venv\Scripts\activate.bat    # Windows Command Prompt

# Start the development server
uvicorn worklog_automation.main:app --reload --host 0.0.0.0 --port 8000

# Or use the direct path (if activation doesn't work)
./venv/Scripts/uvicorn.exe worklog_automation.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Verify Installation

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=worklog_automation --cov-report=html

# Check code quality
ruff check .
ruff format .
mypy .
```

## 📋 Available Dependencies Files

- **requirements.txt**: Core runtime dependencies
- **requirements-dev.txt**: Development and testing dependencies
- **pyproject.toml**: Complete project configuration with optional dependencies

Choose your installation method:

```bash
# Method 1: Using requirements files (recommended for development)
pip install -r requirements.txt -r requirements-dev.txt

# Method 2: Using pyproject.toml
pip install -e ".[dev]"  # Development installation
pip install -e ".[prod]" # Production installation
```

## 📚 API Documentation

Once the server is running, visit:
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/health
- **Metrics** (if enabled): http://localhost:8000/metrics

## ✅ Verification

After starting the server, you should see:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
🚀 Starting Worklog Automation System
Environment: development
Version: 0.1.0
🗄️ Database initialized: sqlite+aiosqlite
✅ Database tables created/verified
📊 Prometheus metrics enabled
🎉 Application startup complete
```

Test the API:
```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs  # or visit in browser
```

## 🏗️ Project Structure

```
worklog_automation/
├── app/
│   ├── api/              # API routes and endpoints
│   ├── core/             # Configuration and security
│   ├── models/           # SQLModel database models
│   ├── schemas/          # Pydantic request/response models
│   ├── services/         # Business logic layer
│   ├── integrations/     # External API integrations
│   └── utils/            # Utility functions
├── tests/                # Comprehensive test suite
├── migrations/           # Alembic database migrations
└── scripts/              # Development and deployment scripts
```

## 🔧 Development

### Virtual Environment Management

```bash
# Activate virtual environment
source venv/Scripts/activate  # Windows (Git Bash)
venv\Scripts\activate.bat      # Windows (Command Prompt)
source venv/bin/activate       # macOS/Linux

# Deactivate virtual environment
deactivate

# Check which Python you're using
which python
python --version

# List installed packages
pip list
pip freeze > requirements-current.txt
```

### Running Tests
```bash
# Make sure virtual environment is activated
source venv/Scripts/activate

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=worklog_automation --cov-report=html

# Run specific test
pytest tests/test_main.py::test_health_check -v

# Run tests with verbose output
pytest tests/ -xvs
```

### Code Quality
```bash
# Activate virtual environment first
source venv/Scripts/activate

# Linting and formatting
ruff check .              # Check for issues
ruff format .             # Format code
ruff check --fix .        # Fix auto-fixable issues

# Type checking
mypy worklog_automation/  # Type check source code

# All quality checks at once
ruff check . && ruff format . && mypy worklog_automation/
```

### Database Management
```bash
# SQLite database file will be created automatically as worklog.db
# For development, you can delete the file to reset the database
rm worklog.db

# The application will recreate tables on startup
# For production with PostgreSQL, use migrations:

# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

### Troubleshooting

#### Virtual Environment Issues
```bash
# If activation doesn't work, try direct execution:
# Windows:
.\venv\Scripts\python.exe -m uvicorn worklog_automation.main:app --reload

# macOS/Linux:
./venv/bin/python -m uvicorn worklog_automation.main:app --reload
```

#### Dependencies Issues
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt -r requirements-dev.txt

# Clear pip cache
pip cache purge

# Upgrade pip
python -m pip install --upgrade pip
```

#### Port Already in Use
```bash
# Use a different port
uvicorn worklog_automation.main:app --reload --port 8001

# Or find and kill the process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:8000 | xargs kill -9
```

## 🌟 Why This Architecture?

### AI-Friendly Design
- **Clear separation of concerns**: Easy for AI to understand and modify
- **Comprehensive type hints**: Full MyPy compatibility
- **Detailed docstrings**: Self-documenting code
- **Consistent naming**: Predictable patterns throughout
- **Modular structure**: Easy to extend and modify

### Developer Experience
- **Hot reload**: Instant feedback during development
- **Rich error messages**: Clear debugging information
- **Automated testing**: Comprehensive test coverage
- **Code quality tools**: Automated linting and formatting
- **Documentation**: Auto-generated API docs

### Production Ready
- **Async throughout**: High performance with asyncio
- **Proper logging**: Structured logging with Loguru
- **Monitoring**: Prometheus metrics and Sentry error tracking
- **Security**: Industry-standard authentication and validation
- **Scalability**: Designed for horizontal scaling

## 📝 Usage Examples

### Basic Time Tracking
```python
# Start work day
POST /api/v1/tracking/start

# Add manual entry
POST /api/v1/tracking/entries
{
    "description": "Implemented user authentication",
    "duration_minutes": 120,
    "project_id": "uuid",
    "commit_hash": "abc123"
}

# Start meeting
POST /api/v1/meetings/start
{
    "title": "Daily Standup",
    "type": "standup"
}
```

### Report Generation
```python
# Get daily report
GET /api/v1/reports/daily/2024-01-15

# Export to Teams
POST /api/v1/integrations/teams/send-report
{
    "date": "2024-01-15",
    "channel_webhook": "https://..."
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run quality checks: `ruff check . && mypy . && pytest`
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on:

- How to set up the development environment
- Code style and quality standards
- Pull request process
- Issue reporting guidelines

### Quick Contribution Steps

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run quality checks: `ruff check . && pytest tests/`
5. Commit your changes: `git commit -m "feat: add amazing feature"`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 🐛 Issues and Support

- **Bug Reports**: [Create an issue](https://github.com/mrahmanashiq/auto-worklog/issues/new?template=bug_report.md)
- **Feature Requests**: [Request a feature](https://github.com/mrahmanashiq/auto-worklog/issues/new?template=feature_request.md)
- **Questions**: [Ask in Discussions](https://github.com/mrahmanashiq/auto-worklog/discussions)

## 📈 Roadmap

- [ ] OAuth2 authentication providers (Google, GitHub, etc.)
- [ ] Mobile app support
- [ ] Advanced analytics and reporting
- [ ] Slack and Discord integrations
- [ ] AI-powered productivity insights
- [ ] Calendar sync improvements
- [ ] Project management integrations (Asana, Trello)

## ⭐ Star History

If you find this project useful, please consider giving it a star on GitHub!

[![Star History Chart](https://api.star-history.com/svg?repos=mrahmanashiq/auto-worklog&type=Date)](https://star-history.com/#mrahmanashiq/auto-worklog&Date)

---

Built with ❤️ for productivity and automation

**Made by developers, for developers** 🚀

