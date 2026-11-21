import unittest
import sys
from pathlib import Path

# Add serenie-kernel/kernel to sys.path
kernel_dir = Path(__file__).resolve().parent.parent.parent / "serenie-kernel" / "kernel"
sys.path.append(str(kernel_dir))

from errors.errors import KernelErrorEngine, KernelErrorCode

class TestStage4ErrorSemantics(unittest.TestCase):
    def setUp(self):
        self.error_engine = KernelErrorEngine()

    def test_kernel_error_atom_emission(self):
        err = self.error_engine.raise_error(
            code=KernelErrorCode.ERR_CONTRACT_VIOLATION,
            message="Contract preconditions failed.",
            context={"file": "sample.py"}
        )
        self.assertEqual(err.code, "ERR-01-CONTRACT-VIOLATION")
        self.assertEqual(err.context["file"], "sample.py")

if __name__ == "__main__":
    unittest.main()
