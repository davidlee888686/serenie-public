"""
Serenie Kernel - Projection Engine
Deterministic view synthesis and multi-format projections.
"""

import json
from typing import Dict, List, Any, Union

class KernelProjectionEngine:
    def build_projection_views(
        self, 
        canonical_data: Union[Dict[str, Any], str], 
        journal_entries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        if isinstance(canonical_data, str):
            try:
                data_obj = json.loads(canonical_data)
            except Exception:
                data_obj = {"raw_text": canonical_data}
        else:
            data_obj = canonical_data

        json_str = json.dumps(data_obj, sort_keys=True, indent=2)
        html_str = f"<html><body><pre>{json_str}</pre></body></html>"
        md_str = f"# Serenie Substrate Projection View\n\n```json\n{json_str}\n```\n"

        ledger_view = [
            {
                "step": idx + 1,
                "event": entry.get("event_type") or entry.get("contract") or "EVENT",
                "hash": entry.get("current_signature") or entry.get("current_hash") or ""
            }
            for idx, entry in enumerate(journal_entries)
        ]

        return {
            "html_view": html_str,
            "json_view": json_str,
            "markdown_view": md_str,
            "ledger_view": ledger_view,
            "journal_block_count": len(journal_entries)
        }
