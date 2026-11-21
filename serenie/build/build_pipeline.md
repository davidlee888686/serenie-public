# Serenie Build Pipeline

Steps:
1. Clean previous builds
2. Run tests
3. Run conformance suite
4. Build release artifacts
5. Generate release manifest
6. Verify release integrity

Commands:
python build_clean.py
pytest
python conformance_runner.py
python build_release.py
python build_verify.py
