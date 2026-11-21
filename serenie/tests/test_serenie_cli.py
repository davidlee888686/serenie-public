import subprocess
import sys
from pathlib import Path

def test_cli_identity():
    # Minimal smoke test
    script = Path('serenie/cli/serenie_cli.py')
    result = subprocess.run([sys.executable, str(script), 'identity', '--input', 'README.md', '--logical-id', 'X', '--version-id', '1'], capture_output=True)
    assert result.returncode == 0
