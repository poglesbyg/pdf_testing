#!/usr/bin/env python3
"""
Test script to demonstrate API functionality
Run the API server first: uv run python api_server.py
"""

import time
import sys
from pathlib import Path
from api_client import PDFSubmissionClient


def test_api():
    """Test the API functionality"""
    print("=" * 60)
    print("PDF SUBMISSION TRACKER API TEST")
    print("=" * 60)
    
    # Initialize client
    print("\n1. Initializing API client...")
    client = PDFSubmissionClient("http://localhost:8000")
    
    # Test health check
    print("\n2. Testing health check...")
    try:
        health = client.health_check()
        print(f"   ✅ API is {health['status']}")
    except Exception as e:
        print(f"   ❌ API is not running. Start it with: uv run python api_server.py")
        print(f"   Error: {e}")
        return False
    
    # Get initial statistics
    print("\n3. Getting database statistics...")
    try:
        stats = client.get_statistics()
        print(f"   Total Submissions: {stats['total_submissions']}")
        print(f"   Total Samples: {stats['total_samples']}")
        print(f"   Unique Projects: {stats['unique_projects']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Check if test PDF exists
    pdf_file = "custom_forms_11095857_1756931956.pdf"
    if not Path(pdf_file).exists():
        print(f"\n❌ Test PDF not found: {pdf_file}")
        print("   Please ensure the test PDF is in the current directory")
        return False
    
    # Check for duplicate
    print(f"\n4. Checking if {pdf_file} is a duplicate...")
    try:
        dup_check = client.check_duplicate(pdf_path=pdf_file)
        if dup_check['is_duplicate']:
            print(f"   ⚠️  File is a duplicate of: {dup_check['existing_submission']['submission_id']}")
            submission_id = dup_check['existing_submission']['submission_id']
        else:
            print("   ✅ File is not a duplicate")
            
            # Process the PDF
            print(f"\n5. Processing PDF: {pdf_file}")
            result = client.process_pdf(pdf_file, save_to_db=True)
            
            if result['success']:
                print(f"   ✅ Successfully processed!")
                print(f"   Submission ID: {result['submission_id']}")
                submission_id = result['submission_id']
            else:
                print(f"   ❌ Processing failed: {result['message']}")
                return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # List submissions
    print("\n6. Listing submissions...")
    try:
        submissions = client.list_submissions(limit=5)
        print(f"   Found {len(submissions)} submission(s):")
        for sub in submissions[:3]:
            print(f"   - {sub['submission_id']} ({sub['total_samples']} samples)")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Search
    print("\n7. Testing search...")
    try:
        search_results = client.search("HTSF")
        print(f"   Found {search_results['count']} result(s) for 'HTSF'")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Get submission details
    if submission_id:
        print(f"\n8. Getting details for submission {submission_id}...")
        try:
            details = client.get_submission(submission_id)
            print(f"   Project: {details['project_id']}")
            print(f"   Owner: {details['owner']}")
            print(f"   Total Samples: {details['total_samples']}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Get samples
        print(f"\n9. Getting samples for submission {submission_id}...")
        try:
            samples = client.get_samples(submission_id)
            stats = samples['statistics']
            print(f"   Total Samples: {stats['total']}")
            print(f"   Avg Concentration: {stats['avg_concentration']:.2f} ng/µL")
            print(f"   Range: {stats['min_concentration']:.2f} - {stats['max_concentration']:.2f} ng/µL")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # List projects
    print("\n10. Listing projects...")
    try:
        projects = client.list_projects()
        print(f"   Found {projects['total']} project(s):")
        for proj in projects['projects']:
            print(f"   - {proj['project_id']}: {proj['count']} submission(s)")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ API TEST COMPLETE!")
    print("=" * 60)
    
    return True


def main():
    """Main function"""
    print("\n⚠️  Note: Make sure the API server is running:")
    print("   Run in another terminal: uv run python api_server.py")
    print("\n   The API will be available at:")
    print("   - API Docs: http://localhost:8000/docs")
    print("   - ReDoc: http://localhost:8000/redoc")
    print("\n   Press Enter to continue with the test...")
    input()
    
    success = test_api()
    
    if success:
        print("\n💡 Tips:")
        print("   - Visit http://localhost:8000/docs for interactive API documentation")
        print("   - Use api_cli.py for command-line access to the API")
        print("   - Use api_client.py to integrate the API into your Python code")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
