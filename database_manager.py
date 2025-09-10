#!/usr/bin/env python3
"""
SQLite database manager for HTSF PDF submissions
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import os

class SubmissionDatabase:
    """Manage PDF submissions in SQLite database"""
    
    def __init__(self, db_path: str = "submissions.db"):
        self.db_path = db_path
        self.conn = None
        self.initialize_database()
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def connect(self):
        """Connect to the database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
        self.conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key support
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def initialize_database(self):
        """Create database tables if they don't exist"""
        self.connect()
        cursor = self.conn.cursor()
        
        # Main submissions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                submission_id TEXT UNIQUE NOT NULL,
                uuid TEXT UNIQUE NOT NULL,
                short_ref TEXT NOT NULL,
                file_hash TEXT NOT NULL,
                project_id TEXT,
                owner TEXT,
                source_organism TEXT,
                sequencing_type TEXT,
                sample_type TEXT,
                total_samples INTEGER,
                pdf_filename TEXT,
                pdf_path TEXT,
                scanned_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(file_hash)
            )
        """)
        
        # Samples table (linked to submissions)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS samples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                submission_id TEXT NOT NULL,
                sample_name TEXT NOT NULL,
                volume_ul REAL,
                qubit_conc REAL,
                nanodrop_conc REAL,
                a260_280_ratio REAL,
                a260_230_ratio REAL,
                FOREIGN KEY (submission_id) REFERENCES submissions(submission_id)
                    ON DELETE CASCADE
            )
        """)
        
        # Additional info table (key-value pairs for flexible storage)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS submission_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                submission_id TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT,
                FOREIGN KEY (submission_id) REFERENCES submissions(submission_id)
                    ON DELETE CASCADE,
                UNIQUE(submission_id, key)
            )
        """)
        
        # Create indexes for better query performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_submissions_project 
            ON submissions(project_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_submissions_file_hash 
            ON submissions(file_hash)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_samples_submission 
            ON samples(submission_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_submission_info_submission 
            ON submission_info(submission_id)
        """)
        
        self.conn.commit()
        self.close()
    
    def save_submission(self, data: Dict) -> bool:
        """
        Save a parsed submission to the database
        Returns True if saved successfully, False if duplicate
        """
        self.connect()
        cursor = self.conn.cursor()
        
        try:
            # Check for duplicate
            file_hash = data['submission_ids']['full_file_hash']
            cursor.execute(
                "SELECT submission_id FROM submissions WHERE file_hash = ?",
                (file_hash,)
            )
            
            if cursor.fetchone():
                self.close()
                return False  # Duplicate found
            
            # Insert main submission record
            cursor.execute("""
                INSERT INTO submissions (
                    submission_id, uuid, short_ref, file_hash,
                    project_id, owner, source_organism,
                    sequencing_type, sample_type, total_samples,
                    pdf_filename, pdf_path, scanned_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['submission_ids']['submission_id'],
                data['submission_ids']['uuid'],
                data['submission_ids']['short_uuid'],
                data['submission_ids']['full_file_hash'],
                data['metadata'].get('project_id'),
                data['metadata'].get('owner'),
                data['metadata'].get('source_organism'),
                data['sequencing'].get('selected_type'),
                data['sample_type'],
                data['total_samples'],
                data['submission_ids']['pdf_filename'],
                data['submission_ids'].get('pdf_path', ''),
                data['submission_ids']['scanned_at']
            ))
            
            submission_id = data['submission_ids']['submission_id']
            
            # Insert samples
            for sample in data['samples']:
                cursor.execute("""
                    INSERT INTO samples (
                        submission_id, sample_name, volume_ul,
                        qubit_conc, nanodrop_conc,
                        a260_280_ratio, a260_230_ratio
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    submission_id,
                    sample['name'],
                    sample['volume_ul'],
                    sample['qubit_conc'],
                    sample['nanodrop_conc'],
                    sample['a260_280_ratio'],
                    sample.get('a260_230_ratio')
                ))
            
            # Insert additional info
            for key, value in data['additional_info'].items():
                # Convert non-string values to JSON
                if not isinstance(value, str):
                    value = json.dumps(value)
                
                cursor.execute("""
                    INSERT INTO submission_info (submission_id, key, value)
                    VALUES (?, ?, ?)
                """, (submission_id, key, value))
            
            self.conn.commit()
            self.close()
            return True
            
        except Exception as e:
            self.conn.rollback()
            self.close()
            raise e
    
    def get_submission(self, submission_id: str = None, uuid: str = None, 
                       file_hash: str = None) -> Optional[Dict]:
        """Get a submission by various identifiers"""
        self.connect()
        cursor = self.conn.cursor()
        
        # Build query based on provided identifier
        if submission_id:
            query = "SELECT * FROM submissions WHERE submission_id = ?"
            params = (submission_id,)
        elif uuid:
            query = "SELECT * FROM submissions WHERE uuid = ?"
            params = (uuid,)
        elif file_hash:
            query = "SELECT * FROM submissions WHERE file_hash = ?"
            params = (file_hash,)
        else:
            self.close()
            return None
        
        cursor.execute(query, params)
        row = cursor.fetchone()
        
        if not row:
            self.close()
            return None
        
        # Convert row to dictionary
        submission = dict(row)
        
        # Get samples
        cursor.execute(
            "SELECT * FROM samples WHERE submission_id = ?",
            (submission['submission_id'],)
        )
        submission['samples'] = [dict(row) for row in cursor.fetchall()]
        
        # Get additional info
        cursor.execute(
            "SELECT key, value FROM submission_info WHERE submission_id = ?",
            (submission['submission_id'],)
        )
        submission['additional_info'] = {}
        for row in cursor.fetchall():
            key = row['key']
            value = row['value']
            # Try to parse JSON values
            try:
                submission['additional_info'][key] = json.loads(value)
            except:
                submission['additional_info'][key] = value
        
        self.close()
        return submission
    
    def check_duplicate(self, file_hash: str) -> Optional[Dict]:
        """Check if a submission with this file hash exists"""
        return self.get_submission(file_hash=file_hash)
    
    def list_submissions(self, project_id: str = None, 
                         limit: int = None) -> List[Dict]:
        """List all submissions, optionally filtered by project"""
        self.connect()
        cursor = self.conn.cursor()
        
        if project_id:
            query = """
                SELECT submission_id, project_id, owner, total_samples, 
                       scanned_at, pdf_filename, short_ref
                FROM submissions 
                WHERE project_id = ?
                ORDER BY scanned_at DESC
            """
            params = (project_id,)
        else:
            query = """
                SELECT submission_id, project_id, owner, total_samples, 
                       scanned_at, pdf_filename, short_ref
                FROM submissions 
                ORDER BY scanned_at DESC
            """
            params = ()
        
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query, params)
        submissions = [dict(row) for row in cursor.fetchall()]
        
        self.close()
        return submissions
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        self.connect()
        cursor = self.conn.cursor()
        
        stats = {}
        
        # Total submissions
        cursor.execute("SELECT COUNT(*) as count FROM submissions")
        stats['total_submissions'] = cursor.fetchone()['count']
        
        # Total samples
        cursor.execute("SELECT COUNT(*) as count FROM samples")
        stats['total_samples'] = cursor.fetchone()['count']
        
        # Unique projects
        cursor.execute("SELECT COUNT(DISTINCT project_id) as count FROM submissions")
        stats['unique_projects'] = cursor.fetchone()['count']
        
        # Submissions by project
        cursor.execute("""
            SELECT project_id, COUNT(*) as count 
            FROM submissions 
            GROUP BY project_id
            ORDER BY count DESC
        """)
        stats['by_project'] = [dict(row) for row in cursor.fetchall()]
        
        # Recent submissions
        cursor.execute("""
            SELECT submission_id, project_id, scanned_at 
            FROM submissions 
            ORDER BY scanned_at DESC 
            LIMIT 5
        """)
        stats['recent_submissions'] = [dict(row) for row in cursor.fetchall()]
        
        # Sample statistics
        cursor.execute("""
            SELECT 
                AVG(nanodrop_conc) as avg_concentration,
                MIN(nanodrop_conc) as min_concentration,
                MAX(nanodrop_conc) as max_concentration
            FROM samples
            WHERE nanodrop_conc > 0
        """)
        concentration_stats = cursor.fetchone()
        stats['concentration_stats'] = dict(concentration_stats) if concentration_stats else {}
        
        self.close()
        return stats
    
    def search_submissions(self, search_term: str) -> List[Dict]:
        """Search submissions by various fields"""
        self.connect()
        cursor = self.conn.cursor()
        
        query = """
            SELECT DISTINCT s.*
            FROM submissions s
            LEFT JOIN submission_info si ON s.submission_id = si.submission_id
            WHERE s.submission_id LIKE ?
               OR s.project_id LIKE ?
               OR s.owner LIKE ?
               OR s.source_organism LIKE ?
               OR s.pdf_filename LIKE ?
               OR si.value LIKE ?
            ORDER BY s.scanned_at DESC
        """
        
        search_pattern = f"%{search_term}%"
        params = tuple([search_pattern] * 6)
        
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        
        self.close()
        return results
    
    def delete_submission(self, submission_id: str) -> bool:
        """Delete a submission and all related data"""
        self.connect()
        cursor = self.conn.cursor()
        
        try:
            cursor.execute(
                "DELETE FROM submissions WHERE submission_id = ?",
                (submission_id,)
            )
            
            affected = cursor.rowcount
            self.conn.commit()
            self.close()
            return affected > 0
            
        except Exception as e:
            self.conn.rollback()
            self.close()
            raise e
    
    def export_to_json(self, output_file: str = "submissions_export.json"):
        """Export all submissions to JSON"""
        submissions = self.list_submissions()
        
        # Get full details for each submission
        full_data = []
        for sub in submissions:
            full_submission = self.get_submission(submission_id=sub['submission_id'])
            full_data.append(full_submission)
        
        with open(output_file, 'w') as f:
            json.dump(full_data, f, indent=2)
        
        return len(full_data)
