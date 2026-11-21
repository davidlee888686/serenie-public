import unittest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent / "runtime"))
from dtr.serenie_substrate import DeterministicRuntimeHost, InvariantContract

class TestDTRSubstrate(unittest.TestCase):
    def setUp(self):
        self.runtime = DeterministicRuntimeHost()
        self.contract = InvariantContract(
            name="Markdown_Sanitization_Gate",
            determinism_level="D_4",
            preconditions={"prevent_placeholders": True}
        )

    def test_dtr_morphic_pass(self):
        source_doc = "# Serenie Kernel\nSystem invariants verified.\n"
        html_out, block_sig = self.runtime.execute_transition("DOC-001", "V1.0", self.contract, source_doc)
        
        self.assertTrue(html_out.startswith("<html>"))
        self.assertIsNotNone(block_sig)
        self.assertTrue(self.runtime.journal.verify_journal_provability())

    def test_dtr_placeholder_rejection(self):
        invalid_doc = "# Serenie Kernel\nTODO: fix placeholder\n"
        with self.assertRaises(ValueError):
            self.runtime.execute_transition("DOC-002", "V1.0", self.contract, invalid_doc)

if __name__ == "__main__":
    unittest.main()
