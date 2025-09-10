# PDF Submission Tracker

A comprehensive Python system for parsing, tracking, and storing HTSF (High Throughput Sequencing Facility) PDF submission forms with SQLite database support.

## Features

### 📄 PDF Parsing
- Extract structured data from HTSF Nanopore submission forms
- Parse sample tables with concentration data
- Extract metadata (project ID, owner, organism, etc.)
- Identify sequencing parameters and additional information
- Clean and format messy PDF text extraction

### 🔑 Unique ID System
- **Submission ID**: Human-readable format (e.g., `HTSFJL147_20250910_113759`)
- **UUID**: Globally unique identifier for each submission
- **Short Reference**: 8-character reference for quick identification
- **File Hash**: SHA256 hash for duplicate detection
- **Timestamp tracking**: Precise scan time recording

### 💾 SQLite Database Storage
- Structured database with normalized tables
- Store submissions, samples, and metadata
- Full-text search capabilities
- Duplicate detection based on file hash
- Database statistics and reporting
- Export to JSON for data interchange

### 🌐 REST API
- FastAPI-based REST API with automatic documentation
- Upload and process PDFs via HTTP
- Query submissions and samples
- Search across all fields
- Export data in multiple formats
- Interactive Swagger UI and ReDoc documentation
- Python client library and CLI tool included

## Installation

```bash
# Install dependencies using uv
uv sync

# Or using pip
pip install pypdf2 fastapi uvicorn python-multipart requests
```

## Usage

### Basic PDF Parsing

```bash
# Parse PDF and save to JSON
uv run python main.py

# Parse PDF and save to SQLite database
uv run python main.py --sqlite

# Parse a specific PDF file
uv run python main.py /path/to/pdf.pdf --sqlite
```

### SQLite Database Management

```bash
# Interactive database query tool
uv run python db_query_tool.py

# Full SQLite tracking demonstration
uv run python sqlite_tracker.py

# Track submissions with duplicate detection
uv run python track_submissions.py
```

### REST API

```bash
# Start the API server
uv run python api_server.py

# API will be available at:
# - http://localhost:8000/docs (Swagger UI)
# - http://localhost:8000/redoc (ReDoc)

# Test the API
uv run python test_api.py

# Use the CLI tool
uv run python api_cli.py --help

# Examples:
uv run python api_cli.py process sample.pdf
uv run python api_cli.py list --limit 10
uv run python api_cli.py search "HTSF"
uv run python api_cli.py stats
```

## Database Schema

### Tables

1. **submissions** - Main submission records
   - Unique IDs (submission_id, uuid, file_hash)
   - Project information
   - Sample counts
   - Timestamps

2. **samples** - Individual sample data
   - Sample names
   - Concentration measurements
   - Quality ratios

3. **submission_info** - Additional metadata
   - Key-value pairs for flexible storage
   - Sequencing parameters
   - Comments and notes

## Example Output

```
SUBMISSION IDENTIFIERS:
  Submission ID: HTSFJL147_20250910_113759
  UUID: eddd5054-143f-45fb-8b59-af599ceb4c4d
  Short Reference: eddd5054
  File Hash: 91ec85627b317eb7...

PROJECT INFORMATION:
  Project: HTSF--JL-147
  Owner: Joshua Leon (Mitchell, Charles Lab)
  Organism: Fungi from plant tissue

SAMPLE STATISTICS:
  Total Samples: 94
  Concentration Range: 112.70 - 468.75 ng/µL
  Average: 276.46 ng/µL
```

## Key Features

✅ **Duplicate Detection** - Automatically detects if a PDF has been processed before  
✅ **Comprehensive Parsing** - Extracts all relevant form data  
✅ **Database Ready** - SQLite storage with full CRUD operations  
✅ **Search Capabilities** - Search by project, owner, organism, etc.  
✅ **Export Options** - Export database to JSON for analysis  
✅ **Interactive Tools** - Query tool for database exploration  

## File Structure

```
pdf_testing/
├── main.py              # Main entry point
├── pdf_parser.py        # PDF parsing logic
├── database_manager.py  # SQLite database operations
├── sqlite_tracker.py    # SQLite-based tracking system
├── db_query_tool.py     # Interactive database query tool
├── track_submissions.py # JSON-based tracking (legacy)
├── api_server.py        # FastAPI REST API server
├── api_client.py        # Python client for the API
├── api_cli.py           # Command-line interface for the API
├── test_api.py          # API test script
├── API_DOCUMENTATION.md # Detailed API documentation
└── submissions.db       # SQLite database (created on first run)
```

## API Examples

### Direct Python Usage
```python
from pdf_parser import HTSFFormParser
from database_manager import SubmissionDatabase

# Parse a PDF
parser = HTSFFormParser("sample.pdf")
data = parser.parse()

# Save to database
db = SubmissionDatabase()
success = db.save_submission(data)

# Check for duplicates
duplicate = db.check_duplicate(file_hash)

# Search submissions
results = db.search_submissions("HTSF")
```

### REST API Client Usage
```python
from api_client import PDFSubmissionClient

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
dup_check = client.check_duplicate(pdf_path="sample.pdf")
```

### REST API Endpoints
```bash
# Process PDF
curl -X POST -F "file=@sample.pdf" http://localhost:8000/api/process

# List submissions
curl http://localhost:8000/api/submissions

# Search
curl "http://localhost:8000/api/search?q=HTSF"

# Get statistics
curl http://localhost:8000/api/statistics
```

## License

MIT
