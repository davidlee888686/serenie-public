import json
from typing import Dict, List, Any

class KernelProjectionEngine:
    def build_projection_views(self, canonical_data: Dict[str, Any], journal_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "html_view": f"<html><body>{json.dumps(canonical_data)}</body></html>",
            "json_view": json.dumps(canonical_data, sort_keys=True),
            "journal_block_count": len(journal_entries)
        }
