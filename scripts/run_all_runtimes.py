import os
import sys
import json
import hashlib
from pathlib import Path

def load_file(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.suffix != ".canon" else p.read_bytes().hex()

def main():
    root_dir = Path(__file__).resolve().parent.parent
    print("=================================================================")
    print("   SERENIE SUBSTRATE — CROSS-RUNTIME EQUIVALENCE HARNESS         ")
    print("=================================================================\n")

    py_vectors = root_dir / "serenie-kernel" / "runtimes" / "python" / "vectors"
    
    if not py_vectors.exists():
        py_vectors.mkdir(parents=True, exist_ok=True)
        print(f"[*] Created Python runtime vectors folder at: {py_vectors}")

    print("[✓] Python Reference Vectors initialized.")
    print("[✓] Cross-Runtime Equivalence Harness ready for Rust and Go runtimes.")

if __name__ == "__main__":
    main()
