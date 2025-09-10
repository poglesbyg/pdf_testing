#!/usr/bin/env python3
"""
SQLite-based PDF submission tracker with advanced features
"""

from pdf_parser import HTSFFormParser
from database_manager import SubmissionDatabase
import os
from datetime import datetime
from typing import Optional, List, Dict

class SQLiteSubmissionTracker:
    """Track PDF submissions using SQLite database"""
    
    def __init__(self, db_path: str = "submissions.db"):
        self.db = SubmissionDatabase(db_path)
    
    def process_pdf(self, pdf_path: str) -> Dict:
        """Process a PDF and save to database"""
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Parse the PDF
        parser = HTSFFormParser(pdf_path)
        data = parser.parse()
        
        # Add the full path to the data
        data['submission_ids']['pdf_path'] = os.path.abspath(pdf_path)
        
        # Check for duplicate
        existing = self.db.check_duplicate(data['submission_ids']['full_file_hash'])
        
        if existing:
            print(f"\n⚠️  DUPLICATE DETECTED!")
            print(f"   This PDF was already processed:")
            print(f"   - Original Submission ID: {existing['submission_id']}")
            print(f"   - Project: {existing['project_id']}")
            print(f"   - Originally Scanned: {existing['scanned_at']}")
            print(f"   - Total Samples: {existing['total_samples']}")
            return {
                'success': False,
                'is_duplicate': True,
                'original': existing,
                'data': data
            }
        
        # Save to database
        success = self.db.save_submission(data)
        
        if success:
            print(f"\n✅ NEW SUBMISSION SAVED TO DATABASE")
            print(f"   - Submission ID: {data['submission_ids']['submission_id']}")
            print(f"   - UUID: {data['submission_ids']['uuid']}")
            print(f"   - Short Reference: {data['submission_ids']['short_uuid']}")
            print(f"   - Project: {data['metadata'].get('project_id', 'Unknown')}")
            print(f"   - Total Samples: {data['total_samples']}")
            print(f"   - Database: submissions.db")
            
            return {
                'success': True,
                'is_duplicate': False,
                'data': data
            }
        else:
            print(f"\n❌ Failed to save submission to database")
            return {
                'success': False,
                'is_duplicate': False,
                'data': data
            }
    
    def list_all_submissions(self, limit: int = None):
        """List all submissions in the database"""
        submissions = self.db.list_submissions(limit=limit)
        
        print("\n" + "=" * 70)
        print("📚 ALL SUBMISSIONS IN DATABASE")
        print("=" * 70)
        
        if not submissions:
            print("No submissions found in database.")
            return
        
        for i, sub in enumerate(submissions, 1):
            print(f"\n{i}. {sub['submission_id']}")
            print(f"   Project: {sub['project_id']}")
            print(f"   Owner: {sub['owner']}")
            print(f"   Samples: {sub['total_samples']}")
            print(f"   Scanned: {sub['scanned_at']}")
            print(f"   Short Ref: {sub['short_ref']}")
            print(f"   File: {sub['pdf_filename']}")
    
    def show_statistics(self):
        """Display database statistics"""
        stats = self.db.get_statistics()
        
        print("\n" + "=" * 70)
        print("📊 DATABASE STATISTICS")
        print("=" * 70)
        
        print(f"\n📈 Overview:")
        print(f"   Total Submissions: {stats['total_submissions']}")
        print(f"   Total Samples: {stats['total_samples']}")
        print(f"   Unique Projects: {stats['unique_projects']}")
        
        if stats['concentration_stats']:
            print(f"\n🧪 Sample Concentration Statistics:")
            print(f"   Average: {stats['concentration_stats']['avg_concentration']:.2f} ng/µL")
            print(f"   Minimum: {stats['concentration_stats']['min_concentration']:.2f} ng/µL")
            print(f"   Maximum: {stats['concentration_stats']['max_concentration']:.2f} ng/µL")
        
        if stats['by_project']:
            print(f"\n📁 Submissions by Project:")
            for proj in stats['by_project']:
                print(f"   - {proj['project_id']}: {proj['count']} submission(s)")
        
        if stats['recent_submissions']:
            print(f"\n🕐 Recent Submissions:")
            for sub in stats['recent_submissions']:
                print(f"   - {sub['submission_id']} ({sub['project_id']}) - {sub['scanned_at']}")
    
    def search_database(self, search_term: str):
        """Search for submissions"""
        results = self.db.search_submissions(search_term)
        
        print(f"\n" + "=" * 70)
        print(f"🔍 SEARCH RESULTS FOR: '{search_term}'")
        print("=" * 70)
        
        if not results:
            print(f"No submissions found matching '{search_term}'")
            return
        
        print(f"Found {len(results)} matching submission(s):")
        
        for i, sub in enumerate(results, 1):
            print(f"\n{i}. {sub['submission_id']}")
            print(f"   Project: {sub['project_id']}")
            print(f"   Owner: {sub['owner']}")
            print(f"   Organism: {sub['source_organism']}")
            print(f"   Samples: {sub['total_samples']}")
            print(f"   File: {sub['pdf_filename']}")
    
    def get_submission_details(self, submission_id: str):
        """Get detailed information about a submission"""
        submission = self.db.get_submission(submission_id=submission_id)
        
        if not submission:
            print(f"\n❌ Submission '{submission_id}' not found")
            return
        
        print(f"\n" + "=" * 70)
        print(f"📋 SUBMISSION DETAILS: {submission_id}")
        print("=" * 70)
        
        print(f"\n🆔 Identifiers:")
        print(f"   Submission ID: {submission['submission_id']}")
        print(f"   UUID: {submission['uuid']}")
        print(f"   Short Ref: {submission['short_ref']}")
        print(f"   File Hash: {submission['file_hash'][:16]}...")
        
        print(f"\n📁 Project Information:")
        print(f"   Project ID: {submission['project_id']}")
        print(f"   Owner: {submission['owner']}")
        print(f"   Source Organism: {submission['source_organism']}")
        
        print(f"\n🧬 Sequencing:")
        print(f"   Type: {submission['sequencing_type']}")
        print(f"   Sample Type: {submission['sample_type']}")
        
        print(f"\n📊 Samples: {submission['total_samples']} total")
        if submission['samples'][:5]:  # Show first 5 samples
            print("   First 5 samples:")
            for sample in submission['samples'][:5]:
                print(f"   - {sample['sample_name']}: {sample['nanodrop_conc']:.2f} ng/µL")
        
        print(f"\n📎 Additional Information:")
        for key, value in submission['additional_info'].items():
            if key not in ['additional_comments']:
                print(f"   {key.replace('_', ' ').title()}: {value}")
        
        if 'additional_comments' in submission['additional_info']:
            print(f"\n💬 Comments:")
            print(f"   {submission['additional_info']['additional_comments']}")
        
        print(f"\n📅 Metadata:")
        print(f"   Scanned: {submission['scanned_at']}")
        print(f"   Database Entry: {submission['created_at']}")
        print(f"   PDF File: {submission['pdf_filename']}")
    
    def export_database(self, output_file: str = "submissions_export.json"):
        """Export database to JSON"""
        count = self.db.export_to_json(output_file)
        print(f"\n✅ Exported {count} submissions to {output_file}")


def main():
    """Demonstrate SQLite database functionality"""
    tracker = SQLiteSubmissionTracker()
    
    print("=" * 70)
    print("SQLITE PDF SUBMISSION TRACKER")
    print("=" * 70)
    
    # Process the PDF
    pdf_file = "custom_forms_11095857_1756931956.pdf"
    print(f"\n1️⃣ Processing PDF: {pdf_file}")
    result = tracker.process_pdf(pdf_file)
    
    # List all submissions
    print("\n2️⃣ Listing all submissions:")
    tracker.list_all_submissions()
    
    # Show statistics
    print("\n3️⃣ Database statistics:")
    tracker.show_statistics()
    
    # Search functionality
    print("\n4️⃣ Search demonstration:")
    tracker.search_database("HTSF")
    
    # Get detailed information
    if result['success']:
        print("\n5️⃣ Getting detailed submission information:")
        tracker.get_submission_details(result['data']['submission_ids']['submission_id'])
    
    # Test duplicate detection
    print("\n6️⃣ Testing duplicate detection:")
    print("   Processing the same PDF again...")
    result2 = tracker.process_pdf(pdf_file)
    
    # Export database
    print("\n7️⃣ Exporting database to JSON:")
    tracker.export_database()
    
    print("\n" + "=" * 70)
    print("✅ SQLite database demonstration complete!")
    print("   Database file: submissions.db")
    print("   Export file: submissions_export.json")
    print("=" * 70)


if __name__ == "__main__":
    main()
