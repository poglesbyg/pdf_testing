#!/usr/bin/env python3
"""
Quick demo of the PDF Submission Tracker API
This shows how to integrate the API into your own applications
"""

from api_client import PDFSubmissionClient
import json


def pretty_print(data, title=""):
    """Pretty print JSON data with a title"""
    if title:
        print(f"\n{title}")
        print("-" * len(title))
    print(json.dumps(data, indent=2))


def main():
    print("=" * 60)
    print("PDF SUBMISSION TRACKER API - INTEGRATION DEMO")
    print("=" * 60)
    
    # Initialize the API client
    # In production, this URL would be your API server address
    api_url = "http://localhost:8000"
    client = PDFSubmissionClient(api_url)
    
    print(f"\nConnecting to API at: {api_url}")
    
    # 1. Check API Health
    try:
        health = client.health_check()
        print(f"✅ API Status: {health['status']}")
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("\nPlease start the API server first:")
        print("  ./start_api.sh")
        print("  or")
        print("  uv run python api_server.py")
        return
    
    # 2. Get Current Statistics
    print("\n" + "=" * 40)
    print("DATABASE OVERVIEW")
    print("=" * 40)
    
    stats = client.get_statistics()
    print(f"Total Submissions: {stats['total_submissions']}")
    print(f"Total Samples: {stats['total_samples']}")
    print(f"Unique Projects: {stats['unique_projects']}")
    
    # 3. List Projects
    projects = client.list_projects()
    if projects['projects']:
        print("\nProjects in Database:")
        for proj in projects['projects']:
            print(f"  • {proj['project_id']}: {proj['count']} submission(s)")
    
    # 4. Recent Submissions
    print("\n" + "=" * 40)
    print("RECENT SUBMISSIONS")
    print("=" * 40)
    
    submissions = client.list_submissions(limit=3)
    if submissions:
        for sub in submissions:
            print(f"\nSubmission: {sub['submission_id']}")
            print(f"  Project: {sub['project_id']}")
            print(f"  Samples: {sub['total_samples']}")
            print(f"  Scanned: {sub['scanned_at']}")
    else:
        print("No submissions found in database")
    
    # 5. Search Example
    print("\n" + "=" * 40)
    print("SEARCH FUNCTIONALITY")
    print("=" * 40)
    
    search_term = "HTSF"
    print(f"\nSearching for: '{search_term}'")
    results = client.search(search_term)
    print(f"Found {results['count']} matching submission(s)")
    
    # 6. Sample Data Analysis
    if submissions:
        print("\n" + "=" * 40)
        print("SAMPLE ANALYSIS")
        print("=" * 40)
        
        # Get detailed sample data for the first submission
        first_submission = submissions[0]
        samples = client.get_samples(first_submission['submission_id'])
        
        print(f"\nAnalyzing: {first_submission['submission_id']}")
        stats = samples['statistics']
        print(f"  Total Samples: {stats['total']}")
        print(f"  Average Concentration: {stats['avg_concentration']:.2f} ng/µL")
        print(f"  Concentration Range: {stats['min_concentration']:.2f} - {stats['max_concentration']:.2f} ng/µL")
        
        # Show first 5 samples
        print("\n  Sample Details (first 5):")
        for sample in samples['samples'][:5]:
            print(f"    • {sample['sample_name']}: {sample['nanodrop_conc']:.2f} ng/µL (ratio: {sample['a260_280_ratio']})")
    
    # 7. Duplicate Detection Example
    print("\n" + "=" * 40)
    print("DUPLICATE DETECTION")
    print("=" * 40)
    
    # Example: Check if a PDF has been processed before
    # In a real scenario, you would have the actual PDF file
    print("\nDuplicate detection prevents re-processing of the same PDF.")
    print("The system uses SHA256 file hashing to identify duplicates.")
    
    # Example of processing a new PDF (commented out as we don't have a new file)
    # result = client.process_pdf("new_submission.pdf", save_to_db=True)
    # if result['is_duplicate']:
    #     print(f"Duplicate detected: {result['message']}")
    # else:
    #     print(f"New submission created: {result['submission_id']}")
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    
    print("\n📚 API Documentation:")
    print(f"  • Swagger UI: {api_url}/docs")
    print(f"  • ReDoc: {api_url}/redoc")
    print(f"  • Full docs: See API_DOCUMENTATION.md")
    
    print("\n💡 Integration Tips:")
    print("  • Use api_client.PDFSubmissionClient for Python integration")
    print("  • Use REST endpoints directly for other languages")
    print("  • Check file hashes before uploading to avoid duplicates")
    print("  • Use the search API for flexible queries")
    print("  • Export data to JSON for external analysis")


if __name__ == "__main__":
    main()
