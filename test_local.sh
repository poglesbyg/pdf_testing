#!/bin/bash

# Test PDF Tracker Locally

# Test if API dependencies are installed
if uv run python -c "import fastapi" 2>/dev/null; then
    printf "✅ Backend dependencies installed\n"
else
    printf "❌ Backend dependencies missing. Run: uv sync\n"
    exit 1
fi

# Test if frontend directory exists
if [ -d "frontend" ]; then
    printf "✅ Frontend directory found\n"
else
    printf "❌ Frontend directory not found\n"
    exit 1
fi

# Check if npm is installed
if command -v npm &> /dev/null; then
    printf "✅ npm is installed\n"
else
    printf "❌ npm is not installed. Please install Node.js\n"
    exit 1
fi

# Check if Docker is installed (optional)
if command -v docker &> /dev/null; then
    printf "✅ Docker is installed (optional)\n"
else
    printf "⚠️  Docker not installed (optional for containerized deployment)\n"
fi

printf "\n📋 Next steps:\n"
printf "1. Start the backend API:\n"
printf "   uv run python api_server.py\n\n"
printf "2. Install frontend dependencies (first time only):\n"
printf "   cd frontend && npm install\n\n"
printf "3. Start the frontend:\n"
printf "   cd frontend && npm start\n\n"
printf "4. Access the application:\n"
printf "   Frontend: http://localhost:3000\n"
printf "   API Docs: http://localhost:8000/docs\n"
