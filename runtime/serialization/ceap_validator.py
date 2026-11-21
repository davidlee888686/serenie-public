import json
import hashlib
from typing import Dict, Any, Tuple

class CEAPConformanceValidator:
    def __init__(self, raw_source_text: str, logical_id: str, version_tag: str):
        self.raw_text = raw_source_text
        self.logical_id = logical_id
        self.version_tag = version_tag

    def clean_and_normalize(self) -> str:
        lines = [line.strip() for line in self.raw_text.splitlines() if line.strip()]
        return "\n".join(lines)

    def compile_to_envelope(self, filepath: str, namespace: str) -> Tuple[Dict[str, Any], bool]:
        normalized_str = self.clean_and_normalize()
        
        if any(marker in normalized_str for marker in ["TODO", "FIXME", "XXX"]):
            return {"error": "Prohibited placeholder tags present inside payload."}, False
            
        canonical_bytes = normalized_str.encode('utf-8')
        content_hash = f"sha256:{hashlib.sha256(canonical_bytes).hexdigest()}"
        
        envelope = {
            "$schema": "https://serenie.org/schemas/v1/ceap.json",
            "ceap_version": "1.0.0",
            "logical_identity": self.logical_id,
            "version_identity": self.version_tag,
            "content_identity": content_hash,
            "artifact_kind": "PythonModule" if filepath.endswith(".py") else "MarkdownDocumentation",
            "metadata": {
                "namespace": namespace,
                "schema_version": "1.0.0",
                "filepath": filepath
            },
            "payload": {
                "encoding": "utf-8",
                "raw_text": normalized_str,
                "tokens": [{"type": "ModuleRoot", "name": "main", "line": 1}]
            },
            "relations": []
        }
        
        return envelope, True
