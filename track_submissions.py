#!/usr/bin/env python3
"""
Example script demonstrating how to track PDF submissions and detect duplicates
using the unique ID system.
"""

from pdf_parser import HTSFFormParser
import json
import os
from datetime import datetime
from typing import Dict, List

class SubmissionTracker:
    """Track PDF submissions and detect duplicates"""
    
    def __init__(self, database_file: str = "submission_database.json"):
        self.database_file = database_file
        self.submissions = self.load_database()
    
    def load_database(self) -> Dict:
        """Load existing submission database"""
        if os.path.exists(self.database_file):
            with open(self.database_file, 'r') as f:
                return json.load(f)
        return {"submissions": []}
    
    def save_database(self):
        """Save submission database"""
        with open(self.database_file, 'w') as f:
            json.dump(self.submissions, f, indent=2)
    
    def process_pdf(self, pdf_path: str) -> Dict:
        """Process a PDF and check for duplicates"""
        parser = HTSFFormParser(pdf_path)
        data = parser.parse()
        
        # Check for duplicate submission
        file_hash = data['submission_ids']['full_file_hash']
        is_duplicate = self.check_duplicate(file_hash)
        
        result = {
            'submission_id': data['submission_ids']['submission_id'],
            'uuid': data['submission_ids']['uuid'],
            'short_ref': data['submission_ids']['short_uuid'],
            'file_hash': file_hash,
            'is_duplicate': is_duplicate,
            'project_id': data['metadata'].get('project_id', 'Unknown'),
            'total_samples': data['total_samples'],
            'scanned_at': data['submission_ids']['scanned_at'],
            'pdf_filename': data['submission_ids']['pdf_filename']
        }
        
        if is_duplicate:
            # Find the original submission
            original = self.find_original_submission(file_hash)
            result['original_submission'] = original
            print(f"\n⚠️  DUPLICATE DETECTED!")
            print(f"   This PDF was already processed:")
            print(f"   - Original Submission ID: {original['submission_id']}")
            print(f"   - Originally Scanned: {original['scanned_at']}")
        else:
            # Add to database
            self.submissions['submissions'].append(result)
            self.save_database()
            print(f"\n✅ NEW SUBMISSION RECORDED")
            print(f"   - Submission ID: {result['submission_id']}")
            print(f"   - Short Reference: {result['short_ref']}")
        
        return result
    
    def check_duplicate(self, file_hash: str) -> bool:
        """Check if a file hash already exists in the database"""
        for submission in self.submissions['submissions']:
            if submission['file_hash'] == file_hash:
                return True
        return False
    
    def find_original_submission(self, file_hash: str) -> Dict:
        """Find the original submission with the same file hash"""
        for submission in self.submissions['submissions']:
            if submission['file_hash'] == file_hash:
                return submission
        return None
    
    def list_submissions(self):
        """List all tracked submissions"""
        print("\n" + "=" * 60)
        print("TRACKED SUBMISSIONS")
        print("=" * 60)
        
        if not self.submissions['submissions']:
            print("No submissions tracked yet.")
            return
        
        for i, sub in enumerate(self.submissions['submissions'], 1):
            print(f"\n{i}. {sub['submission_id']}")
            print(f"   Project: {sub['project_id']}")
            print(f"   Samples: {sub['total_samples']}")
            print(f"   Scanned: {sub['scanned_at']}")
            print(f"   Short Ref: {sub['short_ref']}")
            print(f"   File: {sub['pdf_filename']}")
    
    def get_statistics(self):
        """Get statistics about tracked submissions"""
        total = len(self.submissions['submissions'])
        projects = set(s['project_id'] for s in self.submissions['submissions'])
        total_samples = sum(s['total_samples'] for s in self.submissions['submissions'])
        
        print("\n" + "=" * 60)
        print("SUBMISSION STATISTICS")
        print("=" * 60)
        print(f"  Total Submissions: {total}")
        print(f"  Unique Projects: {len(projects)}")
        print(f"  Total Samples Tracked: {total_samples}")
        
        if projects:
            print("\n  Projects:")
            for project in sorted(projects):
                count = sum(1 for s in self.submissions['submissions'] if s['project_id'] == project)
                print(f"    - {project}: {count} submission(s)")


def main():
    """Example usage of the submission tracker"""
    tracker = SubmissionTracker()
    
    # Process the PDF
    pdf_file = "custom_forms_11095857_1756931956.pdf"
    print(f"Processing: {pdf_file}")
    result = tracker.process_pdf(pdf_file)
    
    # Show all tracked submissions
    tracker.list_submissions()
    
    # Show statistics
    tracker.get_statistics()
    
    # Demonstrate duplicate detection
    print("\n" + "=" * 60)
    print("DUPLICATE DETECTION TEST")
    print("=" * 60)
    print("Processing the same PDF again to demonstrate duplicate detection...")
    result2 = tracker.process_pdf(pdf_file)
    
    if result2['is_duplicate']:
        print(f"\n✓ Duplicate detection working correctly!")
        print(f"  The system recognized this PDF was already processed.")


if __name__ == "__main__":
    main()
