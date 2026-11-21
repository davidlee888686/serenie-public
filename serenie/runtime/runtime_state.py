import json
from pathlib import Path

class SerenieRuntimeState:
    def __init__(self):
        self.state = {
            'canonical': None,
            'identity': None,
            'delta': None,
            'evidence': None,
            'journal': [],
            'replay': None,
            'projection': None
        }

    def save(self, path: str):
        Path(path).write_text(json.dumps(self.state, indent=2))

    def load(self, path: str):
        self.state = json.loads(Path(path).read_text())
