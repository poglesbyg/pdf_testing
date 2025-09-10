# PDF Submission Tracker API Documentation

## Overview

The PDF Submission Tracker API provides a RESTful interface for parsing and tracking HTSF PDF submissions. The API is built with FastAPI and includes automatic interactive documentation.

## Starting the API Server

```bash
# Start the API server
uv run python api_server.py

# The server will run on http://localhost:8000
# API documentation: http://localhost:8000/docs
# Alternative docs: http://localhost:8000/redoc
```

## API Endpoints

### General Endpoints

#### Health Check
```
GET /health
```
Check if the API is running and healthy.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-10T11:45:00.123456"
}
```

### Processing Endpoints

#### Process PDF
```
POST /api/process
```
Upload and process a PDF submission file.

**Parameters:**
- `file` (multipart/form-data): PDF file to upload
- `save_to_db` (query, optional): Save to database (default: true)

**Response:**
```json
{
  "success": true,
  "is_duplicate": false,
  "submission_id": "HTSFJL147_20250910_113759",
  "message": "PDF processed and saved successfully",
  "data": { ... }
}
```

### Submission Management

#### List Submissions
```
GET /api/submissions
```
List all submissions with optional filtering.

**Query Parameters:**
- `project_id` (optional): Filter by project ID
- `limit` (optional): Limit number of results

**Response:**
```json
[
  {
    "submission_id": "HTSFJL147_20250910_113759",
    "uuid": "eddd5054-143f-45fb-8b59-af599ceb4c4d",
    "short_ref": "eddd5054",
    "project_id": "HTSF--JL-147",
    "owner": "Joshua Leon",
    "total_samples": 94,
    "scanned_at": "2025-09-10T11:37:59.369192",
    "pdf_filename": "custom_forms.pdf"
  }
]
```

#### Get Submission Details
```
GET /api/submissions/{submission_id}
```
Get detailed information about a specific submission.

**Response:**
```json
{
  "submission_id": "HTSFJL147_20250910_113759",
  "project_id": "HTSF--JL-147",
  "samples": [...],
  "additional_info": {...},
  ...
}
```

#### Delete Submission
```
DELETE /api/submissions/{submission_id}
```
Delete a submission from the database.

**Response:**
```json
{
  "message": "Submission HTSFJL147_20250910_113759 deleted successfully"
}
```

### Search and Analytics

#### Search Submissions
```
GET /api/search?q={query}
```
Search submissions across multiple fields.

**Response:**
```json
{
  "count": 5,
  "results": [...]
}
```

#### Get Statistics
```
GET /api/statistics
```
Get database statistics and analytics.

**Response:**
```json
{
  "total_submissions": 10,
  "total_samples": 940,
  "unique_projects": 3,
  "by_project": [...],
  "recent_submissions": [...],
  "concentration_stats": {...}
}
```

### Validation

#### Check Duplicate
```
GET /api/check-duplicate?file_hash={hash}
```
Check if a file hash already exists in the database.

**Response:**
```json
{
  "is_duplicate": true,
  "existing_submission": {
    "submission_id": "HTSFJL147_20250910_113759",
    "project_id": "HTSF--JL-147",
    "scanned_at": "2025-09-10T11:37:59"
  }
}
```

### Export

#### Export Database
```
GET /api/export?format=json
```
Export all submissions to JSON format.

**Response:** File download

### Projects and Samples

#### List Projects
```
GET /api/projects
```
List all unique projects in the database.

**Response:**
```json
{
  "total": 3,
  "projects": [
    {"project_id": "HTSF--JL-147", "count": 5},
    {"project_id": "HTSF--AB-123", "count": 3}
  ]
}
```

#### Get Samples
```
GET /api/samples/{submission_id}
```
Get all samples for a specific submission.

**Response:**
```json
{
  "submission_id": "HTSFJL147_20250910_113759",
  "statistics": {
    "total": 94,
    "avg_concentration": 276.46,
    "min_concentration": 112.70,
    "max_concentration": 468.75
  },
  "samples": [...]
}
```

## Using the Python Client

### Installation
```python
from api_client import PDFSubmissionClient
```

### Basic Usage
```python
# Initialize client
client = PDFSubmissionClient("http://localhost:8000")

# Process a PDF
result = client.process_pdf("sample.pdf", save_to_db=True)

# List submissions
submissions = client.list_submissions(limit=10)

# Search
results = client.search("HTSF")

# Get statistics
stats = client.get_statistics()

# Check for duplicate
is_dup = client.check_duplicate(pdf_path="sample.pdf")

# Export database
client.export_database("export.json")
```

## Using the CLI Tool

### Installation
```bash
# Make sure the API server is running first
uv run python api_server.py

# Then use the CLI
uv run python api_cli.py --help
```

### CLI Examples
```bash
# Process a PDF
uv run python api_cli.py process sample.pdf

# List submissions
uv run python api_cli.py list --limit 10

# Search
uv run python api_cli.py search "HTSF"

# Get statistics
uv run python api_cli.py stats

# Check for duplicate
uv run python api_cli.py check-dup sample.pdf

# Export database
uv run python api_cli.py export output.json

# Get submission details
uv run python api_cli.py get HTSFJL147_20250910_113759

# Delete submission
uv run python api_cli.py delete HTSFJL147_20250910_113759 --force
```

## Error Handling

The API returns standard HTTP status codes:

- `200 OK`: Success
- `400 Bad Request`: Invalid input
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error responses include details:
```json
{
  "error": "Not found",
  "details": "Submission HTSFJL147_20250910_113759 not found"
}
```

## Authentication

Currently, the API does not require authentication. In production, you should add:
- API key authentication
- JWT tokens
- Rate limiting
- CORS configuration

## Interactive Documentation

FastAPI provides automatic interactive documentation:

1. **Swagger UI**: http://localhost:8000/docs
   - Interactive API testing
   - Request/response examples
   - Parameter descriptions

2. **ReDoc**: http://localhost:8000/redoc
   - Clean, readable documentation
   - Detailed schema information

## Deployment

For production deployment:

1. Use a production ASGI server:
```bash
pip install gunicorn
gunicorn api_server:app -w 4 -k uvicorn.workers.UvicornWorker
```

2. Add environment configuration:
```python
# .env file
DATABASE_PATH=/path/to/submissions.db
API_KEY=your-secret-key
CORS_ORIGINS=https://your-domain.com
```

3. Use HTTPS with SSL certificates
4. Set up proper logging and monitoring
5. Implement rate limiting and caching

## Testing

Test the API using curl:

```bash
# Health check
curl http://localhost:8000/health

# Get statistics
curl http://localhost:8000/api/statistics

# Process a PDF
curl -X POST -F "file=@sample.pdf" http://localhost:8000/api/process

# Search
curl "http://localhost:8000/api/search?q=HTSF"
```

## Rate Limits

For production, consider implementing rate limits:
- 100 requests per minute for general endpoints
- 10 requests per minute for processing endpoints
- 1000 requests per hour per IP address
