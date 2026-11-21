import os
import ast
import json
import time
import hashlib
import re
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Any, Tuple, Set

class DiscoveryContext:
    EXCLUDED_DIRS = {
        ".git", "__pycache__", "node_modules", ".pytest_cache", 
        "venv", ".venv", "env", "build", "dist", "target"
    }
    SUPPORTED_EXTENSIONS = {".py", ".ts", ".rs", ".go", ".cs", ".md"}

@dataclass(frozen=True)
class DebtMetrics:
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int

class SerenieDiscoveryEngine:
    def __init__(self, workspace_root: str):
        self.root = os.path.abspath(workspace_root)
        self.total_scanned_files = 0
        self.high_debt_regex = re.compile(r"\b(FIXME|XXX)\b")
        self.medium_debt_regex = re.compile(r"\b(TODO|HACK)\b")

    def audit_file_debt(self, filepath: str) -> DebtMetrics:
        critical = 0
        high = 0
        medium = 0
        low = 0
        
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                
            high += len(self.high_debt_regex.findall(content))
            medium += len(self.medium_debt_regex.findall(content))
            
            if filepath.endswith(".py"):
                try:
                    parsed = ast.parse(content)
                    for node in ast.walk(parsed):
                        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                            if not node.name.startswith("_") and ast.get_docstring(node) is None:
                                low += 1
                except Exception:
                    critical += 1
        except Exception:
            critical += 1

        return DebtMetrics(critical, high, medium, low)

    def execute_discovery(self) -> Dict[str, Any]:
        discovered_files = []
        for dirpath, dirnames, filenames in os.walk(self.root):
            dirnames.sort()
            filenames.sort()
            dirnames[:] = [d for d in dirnames if d not in DiscoveryContext.EXCLUDED_DIRS]

            for file in filenames:
                file_ext = Path(file).suffix
                if file_ext in DiscoveryContext.SUPPORTED_EXTENSIONS:
                    full_path = os.path.join(dirpath, file)
                    rel_path = os.path.relpath(full_path, self.root).replace(os.sep, "/")
                    self.total_scanned_files += 1
                    debt = self.audit_file_debt(full_path)
                    
                    discovered_files.append({
                        "node_id": f"SRC::{rel_path}",
                        "filepath": rel_path,
                        "size_bytes": os.path.getsize(full_path),
                        "debt": {
                            "critical": debt.critical_count,
                            "high": debt.high_count,
                            "medium": debt.medium_count,
                            "low": debt.low_count
                        }
                    })

        return {
            "root_path": self.root,
            "total_files": self.total_scanned_files,
            "files": discovered_files
        }
