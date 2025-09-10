from pdf_parser import HTSFFormParser
from database_manager import SubmissionDatabase
import json
import sys
import os

def main():
    """Main function to demonstrate PDF parsing capabilities"""
    
    # Check command line arguments
    use_sqlite = "--sqlite" in sys.argv
    pdf_path = "custom_forms_11095857_1756931956.pdf"
    
    # Check for custom PDF path
    for arg in sys.argv[1:]:
        if arg != "--sqlite" and os.path.exists(arg):
            pdf_path = arg
            break
    
    # Create parser instance
    parser = HTSFFormParser(pdf_path)
    
    # Option 1: Get a clean, formatted summary
    print("=" * 60)
    print("CLEANED UP OUTPUT:")
    print("=" * 60)
    print(parser.get_summary())
    
    # Option 2: Get structured data
    structured_data = parser.parse()
    
    if use_sqlite:
        # Save to SQLite database
        print("\n💾 SAVING TO SQLITE DATABASE...")
        db = SubmissionDatabase()
        
        # Check for duplicate
        existing = db.check_duplicate(structured_data['submission_ids']['full_file_hash'])
        if existing:
            print(f"⚠️  This PDF was already in database: {existing['submission_id']}")
        else:
            success = db.save_submission(structured_data)
            if success:
                print("✅ Saved to SQLite database: submissions.db")
            else:
                print("❌ Failed to save to database")
    else:
        # Save to JSON (default)
        with open('parsed_form_data.json', 'w') as f:
            json.dump(structured_data, f, indent=2)
        print("\n✓ Structured data saved to 'parsed_form_data.json'")
    
    print("\n🔑 Unique Submission IDs Generated:")
    print(f"  - Submission ID: {structured_data['submission_ids']['submission_id']}")
    print(f"  - Short Reference: {structured_data['submission_ids']['short_uuid']}")
    print(f"  - File Hash (for duplicate detection): {structured_data['submission_ids']['file_hash']}")
    
    print("\n📊 Quick Stats:")
    print(f"  - Total samples: {structured_data['total_samples']}")
    print(f"  - Project: {structured_data['metadata']['project_id']}")
    print(f"  - Sample type: {structured_data['sample_type']}")
    
    if use_sqlite:
        print("\n💡 Tip: Use 'python db_query_tool.py' for interactive database queries")


if __name__ == "__main__":
    main()
