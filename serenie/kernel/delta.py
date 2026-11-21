"""
Serenie Kernel - Delta Engine
Deterministic diffing and state transformation analysis.
"""

import json
import hashlib
from dataclasses import dataclass, field
from typing import Dict, Any, Tuple

@dataclass(frozen=True)
class DeltaResult:
    added: Dict[str, Any]
    removed: Dict[str, Any]
    modified: Dict[str, Tuple[Any, Any]]
    delta_hash: str
    has_changes: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "added": self.added,
            "removed": self.removed,
            "modified": {k: [v[0], v[1]] for k, v in self.modified.items()},
            "delta_hash": self.delta_hash,
            "has_changes": self.has_changes
        }

class DeltaEngine:
    def compare(self, before: Dict[str, Any], after: Dict[str, Any]) -> DeltaResult:
        if not isinstance(before, dict) or not isinstance(after, dict):
            before_dict = {"value": before} if not isinstance(before, dict) else before
            after_dict = {"value": after} if not isinstance(after, dict) else after
        else:
            before_dict = before
            after_dict = after

        added = {}
        removed = {}
        modified = {}

        all_keys = sorted(set(before_dict.keys()) | set(after_dict.keys()))

        for k in all_keys:
            if k not in before_dict:
                added[k] = after_dict[k]
            elif k not in after_dict:
                removed[k] = before_dict[k]
            elif before_dict[k] != after_dict[k]:
                modified[k] = (before_dict[k], after_dict[k])

        has_changes = bool(added or removed or modified)
        
        raw_diff_str = json.dumps(
            {"added": added, "removed": removed, "modified": {k: [v[0], v[1]] for k, v in modified.items()}},
            sort_keys=True,
            separators=(",", ":")
        )
        delta_hash = hashlib.sha256(raw_diff_str.encode("utf-8")).hexdigest()

        return DeltaResult(
            added=added,
            removed=removed,
            modified=modified,
            delta_hash=delta_hash,
            has_changes=has_changes
        )
