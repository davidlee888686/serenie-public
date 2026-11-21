import unittest
import sys
from pathlib import Path

# Add serenie-kernel/kernel to sys.path
kernel_dir = Path(__file__).resolve().parent.parent.parent / "serenie-kernel" / "kernel"
sys.path.append(str(kernel_dir))

from replay.replay import KernelReplayEngine
from projection.projection import KernelProjectionEngine

class TestStage3Execution(unittest.TestCase):
    def setUp(self):
        self.replay_engine = KernelReplayEngine()
        self.projection_engine = KernelProjectionEngine()

    def test_replay_sequence(self):
        mock_journal = [{"current_hash": "abc123"}, {"current_hash": "def456"}]
        result = self.replay_engine.replay_journal_sequence(mock_journal)
        self.assertEqual(result["replayed_blocks"], 2)
        self.assertEqual(result["last_signature"], "def456")

    def test_projection_views(self):
        views = self.projection_engine.build_projection_views({"key": "value"}, [])
        self.assertIn("html_view", views)
        self.assertIn("json_view", views)

if __name__ == "__main__":
    unittest.main()
