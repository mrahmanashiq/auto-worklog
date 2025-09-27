# Contributing to Worklog Automation

Thank you for your interest in contributing to the Worklog Automation System! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Git
- A code editor (VS Code recommended)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/auto-worklog.git
   cd auto-worklog
   ```

2. **Set up Virtual Environment**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows
   # source venv/bin/activate    # macOS/Linux
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt -r requirements-dev.txt
   ```

4. **Set up Environment**
   ```bash
   cp .env.example .env
   # Edit .env as needed
   ```

5. **Run Tests**
   ```bash
   pytest tests/ -v
   ```

## 🔧 Development Workflow

### Code Style
We use several tools to maintain code quality:

```bash
# Format code
ruff format .

# Check for issues
ruff check .

# Type checking
mypy worklog_automation/

# Run all checks
ruff check . && ruff format . && mypy worklog_automation/
```

### Testing
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=worklog_automation --cov-report=html

# Run specific test
pytest tests/test_main.py::test_health_check -v
```

### Commit Guidelines
We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or modifying tests
- `chore:` Maintenance tasks

Example:
```bash
git commit -m "feat: add meeting timer functionality"
git commit -m "fix: resolve database connection issue"
git commit -m "docs: update API documentation"
```

## 📋 Pull Request Process

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Write clean, documented code
   - Add tests for new functionality
   - Update documentation as needed

3. **Run Quality Checks**
   ```bash
   ruff check . && ruff format . && mypy worklog_automation/
   pytest tests/ -v
   ```

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: your descriptive commit message"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub.

## 🎯 What to Contribute

### Good First Issues
- Add new API endpoints
- Improve error messages
- Add more comprehensive tests
- Update documentation
- Add new integrations (Slack, Discord, etc.)

### Feature Areas
- **Authentication**: OAuth providers, SSO
- **Integrations**: More external services
- **Reporting**: Advanced analytics and charts
- **Mobile**: REST API improvements for mobile apps
- **AI/ML**: Time prediction, productivity insights

## 🏗️ Project Structure

```
worklog_automation/
├── api/              # API routes and endpoints
│   └── v1/           # API version 1
├── core/             # Core configuration and utilities
├── models/           # Database models
├── schemas/          # Pydantic request/response models
└── main.py           # Application entry point

tests/                # Test suite
docker-compose.yml    # Docker services
requirements*.txt     # Dependencies
```

## 📚 Key Technologies

- **FastAPI**: Modern Python web framework
- **SQLModel**: Database ORM (SQLAlchemy 2.0)
- **Pydantic**: Data validation
- **Pytest**: Testing framework
- **Ruff**: Linting and formatting
- **MyPy**: Type checking

## ❓ Getting Help

- **Issues**: Check existing [GitHub Issues](https://github.com/mrahmanashiq/auto-worklog/issues)
- **Discussions**: Use [GitHub Discussions](https://github.com/mrahmanashiq/auto-worklog/discussions)
- **Documentation**: Refer to the README.md and API docs

## 📜 Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Follow the project's coding standards

Thank you for contributing! 🎉