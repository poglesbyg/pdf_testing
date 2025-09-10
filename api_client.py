#!/usr/bin/env python3
"""
Client library for PDF Submission Tracker API
"""

import requests
import json
from typing import Optional, Dict, List, Any
from pathlib import Path
import hashlib


class PDFSubmissionClient:
    """Client for interacting with the PDF Submission Tracker API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the API client
        
        Args:
            base_url: Base URL of the API server
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def health_check(self) -> Dict[str, Any]:
        """Check if the API is healthy"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def process_pdf(self, pdf_path: str, save_to_db: bool = True) -> Dict[str, Any]:
        """
        Process a PDF file
        
        Args:
            pdf_path: Path to the PDF file
            save_to_db: Whether to save to database or just parse
            
        Returns:
            Processing result with submission data
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        with open(pdf_path, 'rb') as f:
            files = {'file': (pdf_path.name, f, 'application/pdf')}
            params = {'save_to_db': save_to_db}
            
            response = self.session.post(
                f"{self.base_url}/api/process",
                files=files,
                params=params
            )
            response.raise_for_status()
            return response.json()
    
    def list_submissions(self, project_id: Optional[str] = None, 
                        limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List all submissions
        
        Args:
            project_id: Filter by project ID
            limit: Limit number of results
            
        Returns:
            List of submissions
        """
        params = {}
        if project_id:
            params['project_id'] = project_id
        if limit:
            params['limit'] = limit
        
        response = self.session.get(f"{self.base_url}/api/submissions", params=params)
        response.raise_for_status()
        return response.json()
    
    def get_submission(self, submission_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a submission
        
        Args:
            submission_id: The submission ID
            
        Returns:
            Detailed submission data
        """
        response = self.session.get(f"{self.base_url}/api/submissions/{submission_id}")
        response.raise_for_status()
        return response.json()
    
    def delete_submission(self, submission_id: str) -> Dict[str, Any]:
        """
        Delete a submission
        
        Args:
            submission_id: The submission ID to delete
            
        Returns:
            Deletion confirmation
        """
        response = self.session.delete(f"{self.base_url}/api/submissions/{submission_id}")
        response.raise_for_status()
        return response.json()
    
    def search(self, query: str) -> Dict[str, Any]:
        """
        Search submissions
        
        Args:
            query: Search query string
            
        Returns:
            Search results with count and submissions
        """
        params = {'q': query}
        response = self.session.get(f"{self.base_url}/api/search", params=params)
        response.raise_for_status()
        return response.json()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics
        
        Returns:
            Statistics including totals, projects, and recent submissions
        """
        response = self.session.get(f"{self.base_url}/api/statistics")
        response.raise_for_status()
        return response.json()
    
    def check_duplicate(self, pdf_path: str = None, file_hash: str = None) -> Dict[str, Any]:
        """
        Check if a PDF is a duplicate
        
        Args:
            pdf_path: Path to PDF file (will calculate hash)
            file_hash: Pre-calculated file hash
            
        Returns:
            Duplicate check result
        """
        if pdf_path:
            # Calculate file hash
            sha256_hash = hashlib.sha256()
            with open(pdf_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            file_hash = sha256_hash.hexdigest()
        
        if not file_hash:
            raise ValueError("Either pdf_path or file_hash must be provided")
        
        params = {'file_hash': file_hash}
        response = self.session.get(f"{self.base_url}/api/check-duplicate", params=params)
        response.raise_for_status()
        return response.json()
    
    def export_database(self, output_file: str = "export.json", format: str = "json") -> bool:
        """
        Export the database
        
        Args:
            output_file: Output filename
            format: Export format (currently only 'json')
            
        Returns:
            Success status
        """
        params = {'format': format}
        response = self.session.get(f"{self.base_url}/api/export", params=params)
        response.raise_for_status()
        
        # Save the exported file
        with open(output_file, 'wb') as f:
            f.write(response.content)
        
        return True
    
    def list_projects(self) -> Dict[str, Any]:
        """
        List all unique projects
        
        Returns:
            List of projects with submission counts
        """
        response = self.session.get(f"{self.base_url}/api/projects")
        response.raise_for_status()
        return response.json()
    
    def get_samples(self, submission_id: str) -> Dict[str, Any]:
        """
        Get samples for a submission
        
        Args:
            submission_id: The submission ID
            
        Returns:
            Samples data with statistics
        """
        response = self.session.get(f"{self.base_url}/api/samples/{submission_id}")
        response.raise_for_status()
        return response.json()


def main():
    """Example usage of the API client"""
    # Initialize client
    client = PDFSubmissionClient()
    
    print("PDF Submission Tracker API Client")
    print("=" * 60)
    
    # Check API health
    try:
        health = client.health_check()
        print(f"✅ API is {health['status']} at {health['timestamp']}")
    except Exception as e:
        print(f"❌ API is not accessible: {e}")
        return
    
    # Get statistics
    print("\n📊 Database Statistics:")
    stats = client.get_statistics()
    print(f"   Total Submissions: {stats['total_submissions']}")
    print(f"   Total Samples: {stats['total_samples']}")
    print(f"   Unique Projects: {stats['unique_projects']}")
    
    # List recent submissions
    print("\n📋 Recent Submissions:")
    submissions = client.list_submissions(limit=5)
    for sub in submissions:
        print(f"   - {sub['submission_id']} ({sub['project_id']}) - {sub['total_samples']} samples")
    
    # Process a PDF (example - won't run without a valid file)
    pdf_file = "custom_forms_11095857_1756931956.pdf"
    if Path(pdf_file).exists():
        print(f"\n📄 Processing PDF: {pdf_file}")
        
        # Check for duplicate first
        dup_check = client.check_duplicate(pdf_path=pdf_file)
        if dup_check['is_duplicate']:
            print(f"   ⚠️ Duplicate detected: {dup_check['existing_submission']['submission_id']}")
        else:
            print("   ✓ Not a duplicate, processing...")
            result = client.process_pdf(pdf_file, save_to_db=True)
            if result['success']:
                print(f"   ✅ Processed successfully: {result['submission_id']}")
            else:
                print(f"   ❌ Processing failed: {result['message']}")
    
    # Search example
    print("\n🔍 Search Example:")
    search_results = client.search("HTSF")
    print(f"   Found {search_results['count']} results for 'HTSF'")
    
    # List projects
    print("\n📁 Projects in Database:")
    projects = client.list_projects()
    for proj in projects['projects']:
        print(f"   - {proj['project_id']}: {proj['count']} submission(s)")


if __name__ == "__main__":
    main()
