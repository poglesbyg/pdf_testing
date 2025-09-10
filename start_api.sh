#!/bin/bash

# Start script for PDF Submission Tracker API

echo "========================================="
echo "PDF SUBMISSION TRACKER API"
echo "========================================="
echo ""
echo "Starting API server..."
echo ""
echo "The API will be available at:"
echo "  - API Endpoint: http://localhost:8000"
echo "  - Swagger UI:   http://localhost:8000/docs"
echo "  - ReDoc:        http://localhost:8000/redoc"
echo ""
echo "To test the API:"
echo "  1. Open a new terminal"
echo "  2. Run: uv run python test_api.py"
echo ""
echo "To use the CLI:"
echo "  uv run python api_cli.py --help"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================="
echo ""

# Start the API server
uv run python api_server.py
