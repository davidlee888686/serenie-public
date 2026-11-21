import subprocess
import json
from pathlib import Path

from runtime.runtime_engine import SerenieRuntimeEngine

class SerenieOrchestrator:
    def __init__(self):
        self.engine = SerenieRuntimeEngine()

    def ingest(self, path, logical_id, version_id):
        self.engine.ingest(path, logical_id, version_id)
        return self.engine.state.state

    def delta(self, before, after):
        self.engine.delta(before, after)
        return self.engine.state.state['delta']

    def replay(self):
        self.engine.replay()
        return self.engine.state.state['replay']

    def project(self):
        self.engine.project()
        return self.engine.state.state['projection']

    def run_tests(self):
        result = subprocess.run(['pytest', '-q'], capture_output=True, text=True)
        return {
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }

    def run_conformance(self):
        result = subprocess.run(
            ['python', 'serenie/conformance/conformance_runner.py'],
            capture_output=True,
            text=True
        )
        return json.loads(result.stdout)

    def build_release(self):
        result = subprocess.run(
            ['python', 'serenie/build/build_release.py'],
            capture_output=True,
            text=True
        )
        return result.stdout

    def verify_release(self):
        result = subprocess.run(
            ['python', 'serenie/build/build_verify.py'],
            capture_output=True,
            text=True
        )
        return result.stdout

def main():
    orch = SerenieOrchestrator()

    print('=== Serenie Orchestrator ===')
    print('Commands:')
    print('  ingest <file> <logical_id> <version>')
    print('  delta <before.json> <after.json>')
    print('  replay')
    print('  project')
    print('  tests')
    print('  conformance')
    print('  build')
    print('  verify')

if __name__ == '__main__':
    main()
