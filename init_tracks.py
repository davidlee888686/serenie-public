import os
from pathlib import Path

track_directories = [
    # Track A - Standard
    "serenie-spec/specification/volume-0-meta",
    "serenie-spec/specification/volume-1-core-invariants",
    "serenie-spec/specification/volume-2-ontology",
    "serenie-spec/specification/volume-3-formal-model",
    "serenie-spec/specification/volume-4-protocols",
    "serenie-spec/specification/volume-5-execution",
    "serenie-spec/specification/volume-6-conformance",
    "serenie-spec/specification/volume-7-patterns",
    "serenie-spec/specification/volume-8-corpus",
    "serenie-spec/specification/volume-9-proof-obligations",
    "serenie-spec/schemas",
    "serenie-spec/examples",
    "serenie-spec/corpus",
    "serenie-spec/conformance",
    "serenie-spec/adr",
    "serenie-spec/glossary",
    "serenie-spec/traceability",

    # Track B - Kernel
    "serenie-kernel/kernel/canonicalization",
    "serenie-kernel/kernel/identity",
    "serenie-kernel/kernel/contracts",
    "serenie-kernel/kernel/transformation",
    "serenie-kernel/kernel/delta",
    "serenie-kernel/kernel/evidence",
    "serenie-kernel/kernel/journal",
    "serenie-kernel/kernel/replay",
    "serenie-kernel/kernel/projection",
    "serenie-kernel/kernel/errors",
    "serenie-kernel/runtimes/python",
    "serenie-kernel/runtimes/rust",
    "serenie-kernel/runtimes/go",

    # Track C - Tooling
    "serenie-tooling/compiler",
    "serenie-tooling/generators",
    "serenie-tooling/release",

    # Track D - Ecosystem
    "serenie-ecosystem/integrations",
    "serenie-ecosystem/plugins"
]

for d in track_directories:
    p = Path(d)
    p.mkdir(parents=True, exist_ok=True)
    readme = p / "README.md"
    if not readme.exists():
        readme.write_text(f"# {p.name.replace('-', ' ').title()}\n\nTrack directory initialized.\n", encoding="utf-8")

print("Four track repository structures and README stubs initialized.")
