import unittest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent / "runtime"))
from serialization.ceap_validator import CEAPConformanceValidator

class TestCEAPValidator(unittest.TestCase):
    def test_ceap_compilation_success(self):
        sample_code = "import os\ndef start(): return True\n"
        validator = CEAPConformanceValidator(sample_code, "ART-001", "REV-01")
        envelope, success = validator.compile_to_envelope("src/main.py", "serenie.core")
        
        self.assertTrue(success)
        self.assertEqual(envelope["ceap_version"], "1.0.0")
        self.assertTrue(envelope["content_identity"].startswith("sha256:"))

    def test_ceap_placeholder_rejection(self):
        sample_code = "def start():\n    # TODO: implement\n    pass\n"
        validator = CEAPConformanceValidator(sample_code, "ART-002", "REV-01")
        envelope, success = validator.compile_to_envelope("src/main.py", "serenie.core")
        
        self.assertFalse(success)
        self.assertIn("error", envelope)

if __name__ == "__main__":
    unittest.main()
