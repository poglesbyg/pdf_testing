"""
Optimized Database Manager for PDF Submission Tracking
Implements connection pooling and better performance
"""
import sqlite3
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
import threading
import time
from contextlib import contextmanager

class OptimizedSubmissionDatabase:
    """Database manager with connection pooling and performance optimizations"""
    
    # Thread-local storage for connections
    _local = threading.local()
    _lock = threading.Lock()
    
    def __init__(self, db_path: str = "submissions.db"):
        self.db_path = db_path
        self._initialized = False
        self._ensure_initialized()
    
    def _ensure_initialized(self):
        """Lazy initialization of database"""
        if not self._initialized:
            with self._lock:
                if not self._initialized:
                    self._initialize_database()
                    self._initialized = True
    
    @property
    def conn(self):
        """Get or create thread-local connection"""
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            self._local.conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0
            )
            self._local.conn.row_factory = sqlite3.Row
            self._local.conn.execute("PRAGMA foreign_keys = ON")
            # Performance optimizations
            self._local.conn.execute("PRAGMA journal_mode = WAL")
            self._local.conn.execute("PRAGMA synchronous = NORMAL")
            self._local.conn.execute("PRAGMA cache_size = 10000")
            self._local.conn.execute("PRAGMA temp_store = MEMORY")
        return self._local.conn
    
    def connect(self):
        """Compatibility method - connection is managed automatically"""
        return self.conn
    
    def close(self):
        """Close thread-local connection if exists"""
        if hasattr(self._local, 'conn') and self._local.conn:
            self._local.conn.close()
            self._local.conn = None
    
    def close_all(self):
        """Close all connections (call on shutdown)"""
        self.close()
    
    @contextmanager
    def transaction(self):
        """Context manager for transactions"""
        conn = self.conn
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
    
    def _initialize_database(self):
        """Create database tables and indexes if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Main submissions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                submission_id TEXT UNIQUE NOT NULL,
                uuid TEXT UNIQUE NOT NULL,
                short_ref TEXT NOT NULL,
                file_hash TEXT UNIQUE NOT NULL,
                project_id TEXT,
                owner TEXT,
                source_organism TEXT,
                location TEXT,
                total_samples INTEGER,
                sample_type TEXT,
                flowcell_type TEXT,
                kit_type TEXT,
                indexed BOOLEAN,
                concentration_range TEXT,
                scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                pdf_filename TEXT,
                pdf_data BLOB,
                parsed_data TEXT
            )
        """)
        
        # Samples table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS samples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                submission_id TEXT NOT NULL,
                sample_index INTEGER NOT NULL,
                sample_id TEXT,
                concentration REAL,
                ratio_260_280 REAL,
                ratio_260_230 REAL,
                qubit_concentration REAL,
                volume REAL,
                pooling_ratio REAL,
                sequencing_name TEXT,
                FOREIGN KEY (submission_id) REFERENCES submissions(submission_id) ON DELETE CASCADE,
                UNIQUE(submission_id, sample_index)
            )
        """)
        
        # Additional submission info table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS submission_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                submission_id TEXT UNIQUE NOT NULL,
                email TEXT,
                phone TEXT,
                pi_name TEXT,
                billing_info TEXT,
                special_requests TEXT,
                buffer_info TEXT,
                other_info TEXT,
                FOREIGN KEY (submission_id) REFERENCES submissions(submission_id) ON DELETE CASCADE
            )
        """)
        
        # CREATE INDEXES FOR PERFORMANCE
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_submissions_project_id ON submissions(project_id)",
            "CREATE INDEX IF NOT EXISTS idx_submissions_owner ON submissions(owner)",
            "CREATE INDEX IF NOT EXISTS idx_submissions_scanned_at ON submissions(scanned_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_submissions_file_hash ON submissions(file_hash)",
            "CREATE INDEX IF NOT EXISTS idx_submissions_uuid ON submissions(uuid)",
            "CREATE INDEX IF NOT EXISTS idx_submissions_short_ref ON submissions(short_ref)",
            "CREATE INDEX IF NOT EXISTS idx_samples_submission_id ON samples(submission_id)",
            "CREATE INDEX IF NOT EXISTS idx_submission_info_submission_id ON submission_info(submission_id)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        conn.commit()
        conn.close()
    
    def check_duplicate(self, file_content: bytes) -> Optional[Dict]:
        """Check if PDF already exists using SHA256 hash"""
        file_hash = hashlib.sha256(file_content).hexdigest()
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT submission_id, uuid, project_id, owner, scanned_at, pdf_filename
            FROM submissions 
            WHERE file_hash = ?
        """, (file_hash,))
        
        result = cursor.fetchone()
        if result:
            return dict(result)
        return None
    
    def store_submission(self, submission_data: Dict, file_content: bytes, 
                        parsed_data: Dict) -> str:
        """Store a new submission in the database"""
        with self.transaction() as conn:
            cursor = conn.cursor()
            
            # Store main submission
            cursor.execute("""
                INSERT INTO submissions (
                    submission_id, uuid, short_ref, file_hash, project_id, owner,
                    source_organism, location, total_samples, sample_type,
                    flowcell_type, kit_type, indexed, concentration_range,
                    scanned_at, pdf_filename, pdf_data, parsed_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                submission_data['submission_id'],
                submission_data['uuid'],
                submission_data['short_ref'],
                submission_data['file_hash'],
                submission_data.get('project_id'),
                submission_data.get('owner'),
                submission_data.get('source_organism'),
                submission_data.get('location'),
                submission_data.get('total_samples', 0),
                submission_data.get('sample_type'),
                submission_data.get('flowcell_type'),
                submission_data.get('kit_type'),
                submission_data.get('indexed', False),
                submission_data.get('concentration_range'),
                submission_data['scanned_at'],
                submission_data['pdf_filename'],
                file_content,
                json.dumps(parsed_data)
            ))
            
            # Store samples if present
            if 'samples' in parsed_data:
                for idx, sample in enumerate(parsed_data['samples']):
                    cursor.execute("""
                        INSERT INTO samples (
                            submission_id, sample_index, sample_id, concentration,
                            ratio_260_280, ratio_260_230, qubit_concentration,
                            volume, pooling_ratio, sequencing_name
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        submission_data['submission_id'],
                        idx,
                        sample.get('sample_id'),
                        sample.get('concentration'),
                        sample.get('ratio_260_280'),
                        sample.get('ratio_260_230'),
                        sample.get('qubit_concentration'),
                        sample.get('volume'),
                        sample.get('pooling_ratio'),
                        sample.get('sequencing_name')
                    ))
            
            # Store additional info
            if 'additional_info' in parsed_data:
                info = parsed_data['additional_info']
                cursor.execute("""
                    INSERT INTO submission_info (
                        submission_id, email, phone, pi_name, billing_info,
                        special_requests, buffer_info, other_info
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    submission_data['submission_id'],
                    info.get('email'),
                    info.get('phone'),
                    info.get('pi_name'),
                    info.get('billing_info'),
                    info.get('special_requests'),
                    info.get('buffer_info'),
                    info.get('other_info')
                ))
        
        return submission_data['submission_id']
    
    def get_submission(self, submission_id: str = None, uuid: str = None, 
                       file_hash: str = None) -> Optional[Dict]:
        """Get a submission by various identifiers"""
        cursor = self.conn.cursor()
        
        # Use only columns that exist in the current database schema
        query = """
            SELECT submission_id, uuid, short_ref, file_hash, project_id, owner,
                   source_organism, location, total_samples, 
                   scanned_at, pdf_filename
            FROM submissions 
            WHERE 
        """
        
        if submission_id:
            query += "submission_id = ?"
            params = (submission_id,)
        elif uuid:
            query += "uuid = ?"
            params = (uuid,)
        elif file_hash:
            query += "file_hash = ?"
            params = (file_hash,)
        else:
            return None
        
        cursor.execute(query, params)
        result = cursor.fetchone()
        
        if result:
            return dict(result)
        return None
    
    def list_submissions(self, project_id: str = None, 
                         limit: int = None) -> List[Dict]:
        """List all submissions, optionally filtered by project"""
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
        
        return submissions
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        cursor = self.conn.cursor()
        
        stats = {}
        
        # Total submissions
        cursor.execute("SELECT COUNT(*) FROM submissions")
        stats['total_submissions'] = cursor.fetchone()[0]
        
        # Total samples
        cursor.execute("SELECT SUM(total_samples) FROM submissions")
        result = cursor.fetchone()[0]
        stats['total_samples'] = result if result else 0
        
        # Unique projects
        cursor.execute("SELECT COUNT(DISTINCT project_id) FROM submissions WHERE project_id IS NOT NULL")
        stats['unique_projects'] = cursor.fetchone()[0]
        
        # Unique owners
        cursor.execute("SELECT COUNT(DISTINCT owner) FROM submissions WHERE owner IS NOT NULL")
        stats['unique_owners'] = cursor.fetchone()[0]
        
        # Recent submissions (last 7 days)
        cursor.execute("""
            SELECT COUNT(*) FROM submissions 
            WHERE datetime(scanned_at) > datetime('now', '-7 days')
        """)
        stats['recent_submissions'] = cursor.fetchone()[0]
        
        # Most active projects
        cursor.execute("""
            SELECT project_id, COUNT(*) as count 
            FROM submissions 
            WHERE project_id IS NOT NULL
            GROUP BY project_id 
            ORDER BY count DESC 
            LIMIT 5
        """)
        stats['top_projects'] = [
            {'project_id': row[0], 'count': row[1]} 
            for row in cursor.fetchall()
        ]
        
        return stats
    
    def update_submission(self, submission_id: str, updates: Dict) -> bool:
        """Update submission fields"""
        if not updates:
            return False
        
        # Build update query
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values())
        values.append(submission_id)
        
        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE submissions SET {set_clause} WHERE submission_id = ?",
                values
            )
            return cursor.rowcount > 0
    
    def delete_submission(self, submission_id: str) -> bool:
        """Delete a submission and all related data"""
        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM submissions WHERE submission_id = ?", (submission_id,))
            return cursor.rowcount > 0
    
    def search_submissions(self, search_term: str) -> List[Dict]:
        """Search submissions across multiple fields"""
        cursor = self.conn.cursor()
        
        # Use parameterized query for safety
        search_pattern = f"%{search_term}%"
        
        query = """
            SELECT DISTINCT submission_id, project_id, owner, total_samples, 
                   scanned_at, pdf_filename, short_ref
            FROM submissions 
            WHERE project_id LIKE ? 
               OR owner LIKE ?
               OR source_organism LIKE ?
               OR pdf_filename LIKE ?
               OR submission_id LIKE ?
            ORDER BY scanned_at DESC
            LIMIT 100
        """
        
        cursor.execute(query, (search_pattern,) * 5)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_samples(self, submission_id: str) -> List[Dict]:
        """Get all samples for a submission"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT sample_index, sample_id, concentration, ratio_260_280,
                   ratio_260_230, qubit_concentration, volume, pooling_ratio,
                   sequencing_name
            FROM samples
            WHERE submission_id = ?
            ORDER BY sample_index
        """, (submission_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_submission_info(self, submission_id: str) -> Optional[Dict]:
        """Get additional submission info"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT email, phone, pi_name, billing_info, special_requests,
                   buffer_info, other_info
            FROM submission_info
            WHERE submission_id = ?
        """, (submission_id,))
        
        result = cursor.fetchone()
        if result:
            return dict(result)
        return None
