import sqlite3
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

class SQLiteMetadataIndex:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = sqlite3.connect(str(db_path))
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.conn.execute("PRAGMA journal_mode = WAL;")
        self._init_schema()

    def _init_schema(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS kg_artifact (
                    artifact_id TEXT PRIMARY KEY,
                    content_hash TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    byte_size INTEGER NOT NULL,
                    created_at REAL NOT NULL
                );
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS kg_artifact_dependency (
                    artifact_id TEXT NOT NULL,
                    depends_on_hash TEXT NOT NULL,
                    PRIMARY KEY (artifact_id, depends_on_hash),
                    FOREIGN KEY (artifact_id) REFERENCES kg_artifact(artifact_id) ON DELETE CASCADE
                );
            """)

    def record_artifact(self, artifact_id: str, c_hash: str, kind: str, size: int, dependencies: List[str] = None):
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO kg_artifact VALUES (?, ?, ?, ?, ?)",
                (artifact_id, c_hash, kind, size, time.time())
            )
            if dependencies:
                for dep_hash in dependencies:
                    self.conn.execute(
                        "INSERT OR REPLACE INTO kg_artifact_dependency VALUES (?, ?)",
                        (artifact_id, dep_hash)
                    )

    def verify_invariants(self) -> Dict[str, Any]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT d.artifact_id, d.depends_on_hash 
            FROM kg_artifact_dependency d 
            LEFT JOIN kg_artifact a ON d.depends_on_hash = a.content_hash 
            WHERE a.content_hash IS NULL
        """)
        orphans = cursor.fetchall()
        return {
            "inv_sys_005_passed": len(orphans) == 0,
            "orphaned_edges": orphans
        }

    def close(self):
        self.conn.close()
