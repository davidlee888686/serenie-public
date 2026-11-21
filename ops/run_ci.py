import sys
import unittest
from pathlib import Path

def main():
    root_dir = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root_dir))
    print("=================================================================")
    print("      SERENIE SUBSTRATE KERNEL — CONTINUOUS INTEGRATION RUNNER   ")
    print("=================================================================\n")

    loader = unittest.TestLoader()
    suite = loader.discover(str(root_dir / "tests" / "integration"), pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if result.wasSuccessful():
        print("\n[✓] All integration tests passed successfully.")
        sys.exit(0)
    else:
        print("\n[ERROR] Test suite failures detected.")
        sys.exit(1)

if __name__ == "__main__":
    main()
