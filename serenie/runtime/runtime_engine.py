import json
from pathlib import Path

from kernel.canonicalizer import Canonicalizer
from kernel.identity import compute_identity
from kernel.delta import DeltaEngine
from kernel.evidence import create_evidence
from kernel.journal import KernelJournal
from kernel.replay import KernelReplayEngine
from kernel.projection import KernelProjectionEngine

from runtime.runtime_state import SerenieRuntimeState

class SerenieRuntimeEngine:
    def __init__(self):
        self.state = SerenieRuntimeState()
        self.journal = KernelJournal()

    def ingest(self, path: str, logical_id: str, version_id: int):
        data = Path(path).read_bytes()

        canon = Canonicalizer().canonicalize(data)
        ident = compute_identity(logical_id, version_id, canon)
        evidence = create_evidence(logical_id, version_id, ident.content_hash, {})

        self.state.state['canonical'] = canon.decode('utf-8')
        self.state.state['identity'] = ident.to_string()
        self.state.state['evidence'] = evidence.__dict__

        self.journal.append('INGEST', {'logical_id': logical_id, 'version_id': version_id})

    def delta(self, before_path: str, after_path: str):
        before = json.loads(Path(before_path).read_text())
        after = json.loads(Path(after_path).read_text())
        result = DeltaEngine().compare(before, after)
        self.state.state['delta'] = result.__dict__
        self.journal.append('DELTA', result.__dict__)

    def replay(self):
        entries = [e.__dict__ for e in self.journal.entries()]
        result = KernelReplayEngine().replay_journal_sequence(entries)
        self.state.state['replay'] = result
        self.journal.append('REPLAY', result)

    def project(self):
        canonical = json.loads(self.state.state['canonical'])
        entries = [e.__dict__ for e in self.journal.entries()]
        views = KernelProjectionEngine().build_projection_views(canonical, entries)
        self.state.state['projection'] = views
        self.journal.append('PROJECT', views)

    def save_state(self, path: str):
        self.state.save(path)

    def load_state(self, path: str):
        self.state.load(path)
