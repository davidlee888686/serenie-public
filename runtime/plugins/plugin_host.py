import json
import hashlib
import sys
from typing import Dict, Any, List, Optional

class PluginCommunicationHost:
    def __init__(self, plugin_id: str):
        self.plugin_id = plugin_id
        self.capabilities: List[str] = []

    def compute_frame_signature(self, frame_payload: Dict[str, Any]) -> str:
        target = {k: v for k, v in frame_payload.items() if k != "signature"}
        canonical_str = json.dumps(target, sort_keys=True, separators=(',', ':'))
        return f"sha256:{hashlib.sha256(canonical_str.encode('utf-8')).hexdigest()}"

    def verify_incoming_frame(self, frame_payload: Dict[str, Any]) -> bool:
        if "signature" not in frame_payload:
            return False
        provided_signature = frame_payload["signature"]
        return provided_signature == self.compute_frame_signature(frame_payload)

    def execute_handshake(self) -> Dict[str, Any]:
        request_frame = {
            "jsonrpc": "2.0",
            "method": "plugin.negotiate_capabilities",
            "params": {
                "host_version": "1.0.0",
                "required_conformance": "LEVEL_1_CORE"
            },
            "id": "MSG-INIT-01"
        }
        request_frame["signature"] = self.compute_frame_signature(request_frame)
        return request_frame
