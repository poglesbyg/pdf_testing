#!/usr/bin/env python3
"""
FastAPI REST API for PDF Submission Tracker
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Query, Path, Body
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import shutil
import tempfile
import json

from pdf_parser import HTSFFormParser
from database_manager import SubmissionDatabase

# Create FastAPI app
app = FastAPI(
    title="PDF Submission Tracker API",
    description="REST API for parsing and tracking HTSF PDF submissions",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc UI
)

# Add CORS middleware for browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database instance - use DATABASE_PATH environment variable if set
db_path = os.getenv('DATABASE_PATH', 'submissions.db')

# Ensure database directory exists BEFORE initializing database
os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)

print(f"Initializing database at: {db_path}")
db = SubmissionDatabase(db_path)

# Pydantic models for request/response validation
class SubmissionResponse(BaseModel):
    """Response model for submission data"""
    submission_id: str
    uuid: Optional[str] = None
    short_ref: Optional[str] = None
    file_hash: Optional[str] = None
    project_id: Optional[str] = None
    owner: Optional[str] = None
    source_organism: Optional[str] = None
    location: Optional[str] = None
    total_samples: int
    scanned_at: str
    pdf_filename: str

class ProcessResult(BaseModel):
    """Result of processing a PDF"""
    success: bool
    is_duplicate: bool
    submission_id: Optional[str]
    message: str
    data: Optional[Dict[str, Any]]

class Statistics(BaseModel):
    """Database statistics"""
    total_submissions: int
    total_samples: int
    unique_projects: int
    by_project: List[Dict[str, Any]]
    recent_submissions: List[Dict[str, Any]]
    concentration_stats: Dict[str, Any]

class SearchResult(BaseModel):
    """Search result model"""
    count: int
    results: List[SubmissionResponse]

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    details: Optional[str]

# API Endpoints

@app.get("/", tags=["General"])
async def root():
    """API root endpoint with basic information"""
    return {
        "name": "PDF Submission Tracker API",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "process": "/api/process",
            "submissions": "/api/submissions",
            "statistics": "/api/statistics"
        }
    }

@app.get("/health", tags=["General"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/db-test", tags=["General"])
async def database_test():
    """Test database connectivity and status"""
    try:
        db.connect()
        cursor = db.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM submissions")
        count = cursor.fetchone()[0]
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        db.close()
        return {
            "database_path": db.db_path,
            "database_exists": os.path.exists(db.db_path),
            "tables": tables,
            "submission_count": count,
            "status": "connected"
        }
    except Exception as e:
        return {
            "database_path": db.db_path,
            "error": str(e),
            "status": "error"
        }

@app.post("/api/process", response_model=ProcessResult, tags=["Processing"])
async def process_pdf(
    file: UploadFile = File(..., description="PDF file to process"),
    save_to_db: bool = Query(True, description="Save to database (true) or just parse (false)")
):
    """
    Process a PDF submission file
    
    - Upload a PDF file
    - Parse and extract data
    - Optionally save to database
    - Check for duplicates
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        shutil.copyfileobj(file.file, tmp_file)
        tmp_path = tmp_file.name
    
    try:
        # Parse the PDF
        parser = HTSFFormParser(tmp_path)
        data = parser.parse()
        
        # Add original filename to the data
        data['submission_ids']['pdf_filename'] = file.filename
        
        if save_to_db:
            # Check for duplicate
            existing = db.check_duplicate(data['submission_ids']['full_file_hash'])
            
            if existing:
                return ProcessResult(
                    success=False,
                    is_duplicate=True,
                    submission_id=existing['submission_id'],
                    message=f"Duplicate detected. This PDF was already processed as {existing['submission_id']}",
                    data=None
                )
            
            # Save to database
            success = db.save_submission(data)
            
            if success:
                return ProcessResult(
                    success=True,
                    is_duplicate=False,
                    submission_id=data['submission_ids']['submission_id'],
                    message="PDF processed and saved successfully",
                    data=data
                )
            else:
                raise HTTPException(status_code=500, detail="Failed to save to database")
        else:
            # Just parse without saving
            return ProcessResult(
                success=True,
                is_duplicate=False,
                submission_id=data['submission_ids']['submission_id'],
                message="PDF parsed successfully (not saved to database)",
                data=data
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@app.get("/api/submissions", response_model=List[SubmissionResponse], tags=["Submissions"])
async def list_submissions(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Limit number of results")
):
    """
    List all submissions
    
    - Optionally filter by project ID
    - Optionally limit results
    """
    submissions = db.list_submissions(project_id=project_id, limit=limit)
    return submissions

@app.get("/api/submissions/{submission_id}", tags=["Submissions"])
async def get_submission(
    submission_id: str = Path(..., description="Submission ID")
):
    """Get detailed information about a specific submission"""
    submission = db.get_submission(submission_id=submission_id)
    
    if not submission:
        raise HTTPException(status_code=404, detail=f"Submission {submission_id} not found")
    
    return submission

@app.get("/api/submissions/{submission_id}/detailed", tags=["Submissions"])
async def get_detailed_submission(
    submission_id: str = Path(..., description="Submission ID")
):
    """Get comprehensive submission details including samples and all metadata"""
    
    # Get basic submission info
    submission = db.get_submission(submission_id=submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail=f"Submission {submission_id} not found")
    
    # Get samples
    conn = db.conn
    if not conn:
        db.connect()
        conn = db.conn
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM samples 
        WHERE submission_id = ?
        ORDER BY id
    """, (submission_id,))
    
    samples = []
    for row in cursor.fetchall():
        samples.append({
            'name': row['sample_name'],
            'volume_ul': row['volume_ul'],
            'qubit_conc': row['qubit_conc'],
            'nanodrop_conc': row['nanodrop_conc'],
            'a260_280_ratio': row['a260_280_ratio'],
            'a260_230_ratio': row['a260_230_ratio']
        })
    
    # Get additional info
    cursor.execute("""
        SELECT key, value FROM submission_info
        WHERE submission_id = ?
    """, (submission_id,))
    
    additional_info = {}
    for row in cursor.fetchall():
        key = row['key']
        value = row['value']
        # Try to parse JSON values
        try:
            import json
            additional_info[key] = json.loads(value)
        except:
            additional_info[key] = value
    
    # Combine all information
    detailed_submission = {
        **submission,
        'samples': samples,
        'sample_count': len(samples),
        'additional_info': additional_info,
        'submission_ids': {
            'submission_id': submission.get('submission_id'),
            'uuid': submission.get('uuid'),
            'short_ref': submission.get('short_ref'),
            'file_hash': submission.get('file_hash')
        }
    }
    
    return detailed_submission

class UpdateSubmissionRequest(BaseModel):
    """Request model for updating submission data"""
    project_id: Optional[str] = None
    owner: Optional[str] = None
    source_organism: Optional[str] = None
    location: Optional[str] = None
    
@app.put("/api/submissions/{submission_id}", response_model=dict, tags=["Submissions"])
async def update_submission(
    submission_id: str = Path(..., description="Submission ID"),
    update_data: UpdateSubmissionRequest = Body(...)
):
    """
    Update submission metadata
    """
    # Check if submission exists
    existing = db.get_submission(submission_id=submission_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # Prepare update dictionary
    update_dict = {}
    if update_data.project_id is not None:
        update_dict['project_id'] = update_data.project_id
    if update_data.owner is not None:
        update_dict['owner'] = update_data.owner
    if update_data.source_organism is not None:
        update_dict['source_organism'] = update_data.source_organism
    if update_data.location is not None:
        update_dict['location'] = update_data.location
    
    if not update_dict:
        return {"message": "No updates provided", "success": False}
    
    success = db.update_submission(submission_id, update_dict)
    
    if success:
        return {
            "message": "Submission updated successfully",
            "success": True,
            "submission_id": submission_id,
            "updated_fields": list(update_dict.keys())
        }
    else:
        return {"message": "Update failed", "success": False}

@app.delete("/api/submissions/{submission_id}", tags=["Submissions"])
async def delete_submission(
    submission_id: str = Path(..., description="Submission ID to delete")
):
    """Delete a submission from the database"""
    success = db.delete_submission(submission_id)
    
    if success:
        return {"message": f"Submission {submission_id} deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail=f"Submission {submission_id} not found")

@app.get("/api/search", response_model=SearchResult, tags=["Search"])
async def search_submissions(
    q: str = Query(..., min_length=1, description="Search query")
):
    """
    Search submissions by various fields
    
    Searches across:
    - Submission ID
    - Project ID
    - Owner
    - Source organism
    - PDF filename
    - Additional info values
    """
    results = db.search_submissions(q)
    return SearchResult(count=len(results), results=results)

@app.get("/api/statistics", response_model=Statistics, tags=["Statistics"])
async def get_statistics():
    """Get database statistics and analytics"""
    stats = db.get_statistics()
    return stats

@app.get("/api/check-duplicate", tags=["Validation"])
async def check_duplicate(
    file_hash: str = Query(..., description="SHA256 file hash to check")
):
    """Check if a file hash already exists in the database"""
    existing = db.check_duplicate(file_hash)
    
    if existing:
        return {
            "is_duplicate": True,
            "existing_submission": {
                "submission_id": existing['submission_id'],
                "project_id": existing['project_id'],
                "scanned_at": existing['scanned_at']
            }
        }
    else:
        return {"is_duplicate": False}

@app.get("/api/export", tags=["Export"])
async def export_database(
    format: str = Query("json", pattern="^(json|csv)$", description="Export format")
):
    """
    Export all submissions
    
    Currently supports JSON format
    """
    if format == "json":
        export_file = "submissions_export.json"
        count = db.export_to_json(export_file)
        
        if os.path.exists(export_file):
            return FileResponse(
                export_file,
                media_type="application/json",
                filename=export_file,
                headers={"X-Total-Count": str(count)}
            )
        else:
            raise HTTPException(status_code=500, detail="Export failed")
    else:
        raise HTTPException(status_code=400, detail="CSV export not yet implemented")

@app.get("/api/projects", tags=["Projects"])
async def list_projects():
    """List all unique projects in the database"""
    stats = db.get_statistics()
    projects = stats.get('by_project', [])
    
    return {
        "total": len(projects),
        "projects": projects
    }

@app.get("/api/samples/{submission_id}", tags=["Samples"])
async def get_samples(
    submission_id: str = Path(..., description="Submission ID")
):
    """Get all samples for a specific submission"""
    submission = db.get_submission(submission_id=submission_id)
    
    if not submission:
        raise HTTPException(status_code=404, detail=f"Submission {submission_id} not found")
    
    samples = submission.get('samples', [])
    
    # Calculate statistics
    if samples:
        concentrations = [s['nanodrop_conc'] for s in samples if s['nanodrop_conc'] > 0]
        stats = {
            "total": len(samples),
            "avg_concentration": sum(concentrations) / len(concentrations) if concentrations else 0,
            "min_concentration": min(concentrations) if concentrations else 0,
            "max_concentration": max(concentrations) if concentrations else 0
        }
    else:
        stats = {
            "total": 0,
            "avg_concentration": 0,
            "min_concentration": 0,
            "max_concentration": 0
        }
    
    return {
        "submission_id": submission_id,
        "statistics": stats,
        "samples": samples
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Not found", "details": str(exc.detail)}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "details": "An unexpected error occurred"}
    )

if __name__ == "__main__":
    import uvicorn
    print("Starting PDF Submission Tracker API...")
    print("API Documentation: http://localhost:8000/docs")
    print("Alternative docs: http://localhost:8000/redoc")
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)
