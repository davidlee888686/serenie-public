"""
Serenie Kernel - Canonicalization Engine
Guarantees byte-level determinism and NFC unicode normalization across all substrates.
"""

import json
import yaml
import hashlib
import unicodedata
from typing import Dict, Any, Union

class Canonicalizer:
    def canonicalize(self, data: Union[bytes, str]) -> bytes:
        if isinstance(data, str):
            raw_bytes = data.encode("utf-8")
        else:
            raw_bytes = data

        text = self._normalize_encoding(raw_bytes)
        text = self._normalize_line_endings(text)
        text = self._normalize_whitespace(text)
        structured = self._parse_structured(text)
        canonical_str = self._serialize_structured(structured)
        return canonical_str.encode("utf-8")

    def content_identity(self, canonical_bytes: bytes) -> str:
        return f"sha256:{hashlib.sha256(canonical_bytes).hexdigest()}"

    def _normalize_encoding(self, data: bytes) -> str:
        text = data.decode("utf-8", errors="replace")
        return unicodedata.normalize("NFC", text)

    def _normalize_line_endings(self, text: str) -> str:
        return text.replace("\r\n", "\n").replace("\r", "\n")

    def _normalize_whitespace(self, text: str) -> str:
        lines = [line.rstrip() for line in text.split("\n")]
        return "\n".join(lines).strip()

    def _parse_structured(self, text: str) -> Any:
        try:
            return json.loads(text)
        except Exception:
            try:
                parsed = yaml.safe_load(text)
                if isinstance(parsed, (dict, list)):
                    return parsed
                return text
            except Exception:
                return text

    def _serialize_structured(self, obj: Any) -> str:
        if isinstance(obj, (dict, list)):
            return json.dumps(
                obj,
                sort_keys=True,
                ensure_ascii=False,
                separators=(",", ":")
            )
        return str(obj)

class SubstrateCanonicalizer:
    @staticmethod
    def normalize_text(raw_data: str) -> Dict[str, Any]:
        canon = Canonicalizer()
        canon_bytes = canon.canonicalize(raw_data)
        normalized_str = canon_bytes.decode("utf-8")
        return {
            "canonical_bytes_len": len(canon_bytes),
            "raw_text": normalized_str,
            "hash_fingerprint": hashlib.sha256(canon_bytes).hexdigest()
        }
