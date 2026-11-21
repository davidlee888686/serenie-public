import json
import yaml
import hashlib
import unicodedata

class Canonicalizer:
    def canonicalize(self, data: bytes) -> bytes:
        text = self._normalize_encoding(data)
        text = self._normalize_line_endings(text)
        text = self._normalize_whitespace(text)
        structured = self._parse_structured(text)
        canonical = self._serialize_structured(structured)
        return canonical.encode("utf-8")

    def content_identity(self, canonical_bytes: bytes) -> str:
        return f"sha256:{hashlib.sha256(canonical_bytes).hexdigest()}"

    def _normalize_encoding(self, data: bytes) -> str:
        text = data.decode("utf-8", errors="replace")
        return unicodedata.normalize("NFC", text)

    def _normalize_line_endings(self, text: str) -> str:
        return text.replace("\r\n", "\n").replace("\r", "\n")

    def _normalize_whitespace(self, text: str) -> str:
        lines = [line.rstrip() for line in text.split("\n")]
        return "\n".join(lines)

    def _parse_structured(self, text: str):
        try:
            return json.loads(text)
        except Exception:
            try:
                return yaml.safe_load(text)
            except Exception:
                return text

    def _serialize_structured(self, obj) -> str:
        if isinstance(obj, dict):
            return json.dumps(obj, sort_keys=True, separators=(",", ":"))
        return str(obj)
