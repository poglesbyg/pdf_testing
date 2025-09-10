#!/usr/bin/env python3
"""
Interactive query tool for the submissions SQLite database
"""

import sqlite3
import json
from database_manager import SubmissionDatabase
from sqlite_tracker import SQLiteSubmissionTracker
import sys

def show_menu():
    """Display interactive menu"""
    print("\n" + "=" * 60)
    print("SUBMISSIONS DATABASE QUERY TOOL")
    print("=" * 60)
    print("1. List all submissions")
    print("2. Search submissions")
    print("3. View submission details")
    print("4. Show database statistics")
    print("5. List submissions by project")
    print("6. Show database schema")
    print("7. Export to JSON")
    print("8. Process new PDF")
    print("9. Delete submission")
    print("0. Exit")
    print("-" * 60)

def show_schema():
    """Display database schema"""
    conn = sqlite3.connect("submissions.db")
    cursor = conn.cursor()
    
    print("\n📊 DATABASE SCHEMA")
    print("=" * 60)
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        print(f"\n📁 Table: {table_name}")
        print("-" * 40)
        
        # Get table structure
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            is_null = "NOT NULL" if col[3] == 0 else "NULL"
            is_pk = "PRIMARY KEY" if col[5] else ""
            
            print(f"   {col_name:25} {col_type:15} {is_null:10} {is_pk}")
    
    # Show indexes
    print("\n🔍 INDEXES")
    print("-" * 40)
    cursor.execute("SELECT name, tbl_name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'")
    indexes = cursor.fetchall()
    for idx in indexes:
        print(f"   {idx[0]:30} on table {idx[1]}")
    
    conn.close()

def main():
    """Main interactive loop"""
    tracker = SQLiteSubmissionTracker()
    db = SubmissionDatabase()
    
    while True:
        show_menu()
        choice = input("\nEnter your choice (0-9): ").strip()
        
        if choice == "0":
            print("\n👋 Goodbye!")
            break
        
        elif choice == "1":
            tracker.list_all_submissions()
        
        elif choice == "2":
            search_term = input("Enter search term: ").strip()
            if search_term:
                tracker.search_database(search_term)
        
        elif choice == "3":
            submission_id = input("Enter submission ID: ").strip()
            if submission_id:
                tracker.get_submission_details(submission_id)
        
        elif choice == "4":
            tracker.show_statistics()
        
        elif choice == "5":
            project_id = input("Enter project ID (or press Enter for all): ").strip()
            submissions = db.list_submissions(project_id=project_id if project_id else None)
            
            print(f"\n📁 Submissions for project: {project_id if project_id else 'All'}")
            print("-" * 60)
            for sub in submissions:
                print(f"• {sub['submission_id']} - {sub['total_samples']} samples - {sub['scanned_at']}")
        
        elif choice == "6":
            show_schema()
        
        elif choice == "7":
            filename = input("Enter export filename (default: submissions_export.json): ").strip()
            if not filename:
                filename = "submissions_export.json"
            tracker.export_database(filename)
        
        elif choice == "8":
            pdf_path = input("Enter PDF file path: ").strip()
            if pdf_path:
                try:
                    tracker.process_pdf(pdf_path)
                except FileNotFoundError as e:
                    print(f"\n❌ Error: {e}")
        
        elif choice == "9":
            submission_id = input("Enter submission ID to delete: ").strip()
            if submission_id:
                confirm = input(f"Are you sure you want to delete {submission_id}? (yes/no): ").strip().lower()
                if confirm == "yes":
                    if db.delete_submission(submission_id):
                        print(f"✅ Submission {submission_id} deleted")
                    else:
                        print(f"❌ Submission {submission_id} not found")
        
        else:
            print("\n❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!")
        sys.exit(0)
