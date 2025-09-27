# 🚀 Getting Started with Worklog Automation System

Welcome to your AI-friendly worklog automation system! This guide will help you get up and running quickly.

## 📋 Prerequisites

- Python 3.11 or higher
- Git (for version control integration)
- Optional: PostgreSQL (SQLite is used by default for development)
- Optional: Redis (for background tasks)

## 🛠️ Installation

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd worklog-automation

# Install the package in development mode
pip install -e ".[dev]"

# Copy environment configuration
cp .env.example .env
```

### 2. Configure Environment

Edit the `.env` file with your settings:

```bash
# Basic configuration
SECRET_KEY="your-super-secret-key-here"
WORK_START_TIME="08:00"
WORK_END_TIME="18:00"

# Integration settings (optional)
TEAMS_WEBHOOK_URL="your-teams-webhook-url"
JIRA_BASE_URL="https://your-company.atlassian.net"
```

### 3. Initialize Database

```bash
# Create database tables
worklog db-create

# Optional: Create test data
worklog dev-data
```

## 🏃 Quick Start

### Start the Server

```bash
# Start development server
worklog serve

# Or use the startup script
./scripts/start.sh
```

The application will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📖 Core Usage

### 1. Start Your Work Day

```bash
curl -X POST "http://localhost:8000/api/v1/tracking/start" \
  -H "Content-Type: application/json" \
  -d '{"initial_activity": "Starting work on authentication module"}'
```

### 2. Start a Meeting Timer

```bash
curl -X POST "http://localhost:8000/api/v1/meetings/start" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Daily Standup",
    "meeting_type": "standup",
    "attendee_count": 5
  }'
```

### 3. Add Manual Time Entry

```bash
curl -X POST "http://localhost:8000/api/v1/tracking/entry" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Implemented JWT authentication",
    "duration_minutes": 120,
    "commit_hash": "abc123",
    "tags": ["backend", "security"]
  }'
```

### 4. Check Current Status

```bash
curl "http://localhost:8000/api/v1/tracking/status"
```

### 5. Stop Meeting

```bash
curl -X POST "http://localhost:8000/api/v1/meetings/{meeting_id}/stop"
```

### 6. End Work Day

```bash
curl -X POST "http://localhost:8000/api/v1/tracking/stop"
```

## 🔧 CLI Commands

The system includes a powerful CLI for management:

```bash
# Server management
worklog serve                    # Start development server
worklog serve --port 8080        # Start on different port

# Database management
worklog db-create               # Create database tables
worklog db-reset                # Reset database (deletes all data!)
worklog db-status               # Check database connection

# User management
worklog create-user --email user@example.com --username johndoe --password secret123

# Configuration
worklog config                  # Show current configuration
worklog validate                # Validate setup and configuration

# Development
worklog dev-data                # Create test data for development
```

## 📱 Daily Workflow Example

Here's a typical workday workflow:

```bash
# 8:00 AM - Start work day
curl -X POST "localhost:8000/api/v1/tracking/start" \
  -d '{"initial_activity": "Checking emails and planning day"}'

# 9:00 AM - Start standup meeting
curl -X POST "localhost:8000/api/v1/meetings/start" \
  -d '{"title": "Daily Standup", "meeting_type": "standup"}'

# 9:30 AM - Stop meeting
curl -X POST "localhost:8000/api/v1/meetings/{meeting_id}/stop"

# 10:00 AM - Log completed work
curl -X POST "localhost:8000/api/v1/tracking/entry" \
  -d '{
    "description": "Fixed authentication bug in login flow",
    "duration_minutes": 90,
    "commit_hash": "a1b2c3d4",
    "jira_ticket": "AUTH-123"
  }'

# 6:00 PM - End work day
curl -X POST "localhost:8000/api/v1/tracking/stop"
```

## 🔗 Integration Setup

### Microsoft Teams

1. Create an incoming webhook in your Teams channel
2. Add the webhook URL to your `.env` file:
   ```
   TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/...
   TEAMS_ENABLED=true
   ```

### Jira

1. Generate an API token in your Atlassian account
2. Configure Jira settings in `.env`:
   ```
   JIRA_BASE_URL=https://your-company.atlassian.net
   JIRA_USERNAME=your-email@company.com
   JIRA_API_TOKEN=your-api-token
   JIRA_ENABLED=true
   ```

## 🧪 Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=worklog_automation

# Run specific test file
pytest tests/test_tracking.py -v
```

### Code Quality

```bash
# Linting and formatting
ruff check .                    # Check for issues
ruff format .                   # Format code

# Type checking
mypy .                          # Type checking
```

### Development Server

```bash
# Start with auto-reload
worklog serve --reload

# Start with specific configuration
worklog serve --host 0.0.0.0 --port 8080 --workers 4
```

## 📊 Monitoring

### Health Checks

```bash
# Basic health check
curl http://localhost:8000/health

# Database status
worklog db-status

# Configuration validation
worklog validate
```

### Logs

Logs are written to the `logs/` directory:
- `worklog_automation.log` - Main application log
- `errors.log` - Error-level logs
- `access.log` - HTTP access logs
- `integrations.log` - External integration logs

## 🐳 Docker Deployment

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

### Production Deployment

```bash
# Build production image
docker build -t worklog-automation .

# Run with production settings
docker run -d \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e DATABASE_URL=postgresql://... \
  worklog-automation
```

## ❓ Troubleshooting

### Common Issues

1. **Database connection fails**
   ```bash
   worklog db-status  # Check connection
   worklog validate   # Validate configuration
   ```

2. **Import errors**
   ```bash
   pip install -e ".[dev]"  # Reinstall in development mode
   ```

3. **Permission errors**
   ```bash
   chmod +x scripts/start.sh  # Make scripts executable
   ```

### Getting Help

- Check the logs in the `logs/` directory
- Use `worklog validate` to check configuration
- Visit http://localhost:8000/docs for API documentation
- Enable debug logging by setting `LOG_LEVEL=DEBUG` in `.env`

## 🎯 Next Steps

1. **Set up integrations** - Configure Teams and Jira webhooks
2. **Customize work schedule** - Adjust work hours in settings
3. **Create projects** - Organize your work with projects
4. **Set up automation** - Configure auto-reports and notifications
5. **Build frontend** - Create a React/Next.js interface

Happy tracking! 🚀

