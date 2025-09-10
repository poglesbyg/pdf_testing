#!/usr/bin/env python3
"""
Command-line interface for the PDF Submission Tracker API
"""

import argparse
import json
import sys
from pathlib import Path
from api_client import PDFSubmissionClient


def print_json(data, indent=2):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=indent))


def main():
    parser = argparse.ArgumentParser(
        description="PDF Submission Tracker API CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a PDF
  python api_cli.py process file.pdf
  
  # List all submissions
  python api_cli.py list
  
  # Search submissions
  python api_cli.py search "HTSF"
  
  # Get submission details
  python api_cli.py get HTSFJL147_20250910_113759
  
  # Get statistics
  python api_cli.py stats
  
  # Check for duplicate
  python api_cli.py check-dup file.pdf
  
  # Export database
  python api_cli.py export output.json
        """
    )
    
    parser.add_argument(
        '--api-url',
        default='http://localhost:8000',
        help='API base URL (default: http://localhost:8000)'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output raw JSON'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Process a PDF file')
    process_parser.add_argument('pdf_file', help='Path to PDF file')
    process_parser.add_argument('--no-save', action='store_true', help='Parse only, do not save to database')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List submissions')
    list_parser.add_argument('--project', help='Filter by project ID')
    list_parser.add_argument('--limit', type=int, help='Limit results')
    
    # Get command
    get_parser = subparsers.add_parser('get', help='Get submission details')
    get_parser.add_argument('submission_id', help='Submission ID')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a submission')
    delete_parser.add_argument('submission_id', help='Submission ID')
    delete_parser.add_argument('--force', action='store_true', help='Skip confirmation')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search submissions')
    search_parser.add_argument('query', help='Search query')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Get statistics')
    
    # Check duplicate command
    checkdup_parser = subparsers.add_parser('check-dup', help='Check for duplicate')
    checkdup_parser.add_argument('pdf_file', help='Path to PDF file')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export database')
    export_parser.add_argument('output_file', help='Output file path')
    
    # Projects command
    projects_parser = subparsers.add_parser('projects', help='List projects')
    
    # Samples command
    samples_parser = subparsers.add_parser('samples', help='Get samples for submission')
    samples_parser.add_argument('submission_id', help='Submission ID')
    
    # Health command
    health_parser = subparsers.add_parser('health', help='Check API health')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize client
    client = PDFSubmissionClient(args.api_url)
    
    try:
        # Execute commands
        if args.command == 'health':
            result = client.health_check()
            if args.json:
                print_json(result)
            else:
                print(f"✅ API is {result['status']} at {result['timestamp']}")
        
        elif args.command == 'process':
            if not Path(args.pdf_file).exists():
                print(f"❌ File not found: {args.pdf_file}")
                sys.exit(1)
            
            result = client.process_pdf(args.pdf_file, save_to_db=not args.no_save)
            if args.json:
                print_json(result)
            else:
                if result['success']:
                    if result['is_duplicate']:
                        print(f"⚠️  Duplicate: {result['message']}")
                    else:
                        print(f"✅ Success: {result['submission_id']}")
                        print(f"   Message: {result['message']}")
                else:
                    print(f"❌ Failed: {result['message']}")
        
        elif args.command == 'list':
            submissions = client.list_submissions(
                project_id=args.project,
                limit=args.limit
            )
            if args.json:
                print_json(submissions)
            else:
                print(f"Found {len(submissions)} submission(s):")
                for sub in submissions:
                    print(f"  • {sub['submission_id']} - {sub['project_id']} - {sub['total_samples']} samples")
        
        elif args.command == 'get':
            submission = client.get_submission(args.submission_id)
            if args.json:
                print_json(submission)
            else:
                print(f"Submission: {submission['submission_id']}")
                print(f"Project: {submission['project_id']}")
                print(f"Owner: {submission['owner']}")
                print(f"Samples: {submission['total_samples']}")
                print(f"Scanned: {submission['scanned_at']}")
                if 'additional_info' in submission:
                    print("\nAdditional Info:")
                    for key, value in submission['additional_info'].items():
                        print(f"  {key}: {value}")
        
        elif args.command == 'delete':
            if not args.force:
                confirm = input(f"Delete submission {args.submission_id}? (y/N): ")
                if confirm.lower() != 'y':
                    print("Cancelled")
                    return
            
            result = client.delete_submission(args.submission_id)
            if args.json:
                print_json(result)
            else:
                print(f"✅ {result['message']}")
        
        elif args.command == 'search':
            results = client.search(args.query)
            if args.json:
                print_json(results)
            else:
                print(f"Found {results['count']} result(s) for '{args.query}':")
                for sub in results['results']:
                    print(f"  • {sub['submission_id']} - {sub['project_id']}")
        
        elif args.command == 'stats':
            stats = client.get_statistics()
            if args.json:
                print_json(stats)
            else:
                print("Database Statistics:")
                print(f"  Total Submissions: {stats['total_submissions']}")
                print(f"  Total Samples: {stats['total_samples']}")
                print(f"  Unique Projects: {stats['unique_projects']}")
                
                if stats['by_project']:
                    print("\nBy Project:")
                    for proj in stats['by_project']:
                        print(f"  • {proj['project_id']}: {proj['count']}")
                
                if stats['recent_submissions']:
                    print("\nRecent Submissions:")
                    for sub in stats['recent_submissions'][:5]:
                        print(f"  • {sub['submission_id']} - {sub['scanned_at']}")
        
        elif args.command == 'check-dup':
            if not Path(args.pdf_file).exists():
                print(f"❌ File not found: {args.pdf_file}")
                sys.exit(1)
            
            result = client.check_duplicate(pdf_path=args.pdf_file)
            if args.json:
                print_json(result)
            else:
                if result['is_duplicate']:
                    print(f"⚠️  Duplicate found:")
                    print(f"   Submission: {result['existing_submission']['submission_id']}")
                    print(f"   Project: {result['existing_submission']['project_id']}")
                    print(f"   Scanned: {result['existing_submission']['scanned_at']}")
                else:
                    print("✅ Not a duplicate")
        
        elif args.command == 'export':
            success = client.export_database(args.output_file)
            if success:
                print(f"✅ Exported to {args.output_file}")
            else:
                print("❌ Export failed")
        
        elif args.command == 'projects':
            projects = client.list_projects()
            if args.json:
                print_json(projects)
            else:
                print(f"Found {projects['total']} project(s):")
                for proj in projects['projects']:
                    print(f"  • {proj['project_id']}: {proj['count']} submission(s)")
        
        elif args.command == 'samples':
            samples = client.get_samples(args.submission_id)
            if args.json:
                print_json(samples)
            else:
                stats = samples['statistics']
                print(f"Samples for {samples['submission_id']}:")
                print(f"  Total: {stats['total']}")
                print(f"  Avg Concentration: {stats['avg_concentration']:.2f} ng/µL")
                print(f"  Range: {stats['min_concentration']:.2f} - {stats['max_concentration']:.2f} ng/µL")
                
                print("\nFirst 10 samples:")
                for sample in samples['samples'][:10]:
                    print(f"  • {sample['sample_name']}: {sample['nanodrop_conc']:.2f} ng/µL")
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to API at {args.api_url}")
        print("   Make sure the API server is running: python api_server.py")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"❌ Not found: {e.response.json().get('detail', 'Resource not found')}")
        else:
            print(f"❌ HTTP Error {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import requests  # Import here to check if installed
    main()
