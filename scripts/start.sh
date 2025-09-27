#!/bin/bash
set -e

echo "🚀 Starting Worklog Automation System"

# Create necessary directories
mkdir -p logs uploads exports

# Check if database needs initialization
echo "📊 Checking database..."
python -m worklog_automation.cli db-status || {
    echo "🔧 Initializing database..."
    python -m worklog_automation.cli db-create
}

# Start the application
echo "🌟 Starting FastAPI server..."
exec python -m worklog_automation.cli serve

