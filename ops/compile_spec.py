import os
import re
import json
import sys
from pathlib import Path

def main():
    root_dir = Path(__file__).resolve().parent.parent
    spec_dir = root_dir / "engineering_os"
    
    print("=================================================================")
    print("      SERENIE SUBSTRATE KERNEL — SPECIFICATION COMPILER          ")
    print("=================================================================\n")

    inv_regex = re.compile(r"\b(INV-[A-Z0-9_-]+)\b")
    po_regex = re.compile(r"\b(PO-[A-Z0-9_-]+)\b")
    conf_regex = re.compile(r"\b(CONF-[A-Z0-9_-]+)\b")
    adr_regex = re.compile(r"\b(ADR-[0-9]{4})\b")

    traceability_map = {
        "invariants": [],
        "proof_obligations": [],
        "conformance_requirements": [],
        "adrs": []
    }

    for path in spec_dir.rglob("*.md"):
        content = path.read_text(encoding="utf-8", errors="ignore")
        rel_path = path.relative_to(root_dir).as_posix()

        for match in inv_regex.findall(content):
            traceability_map["invariants"].append({"id": match, "file": rel_path})
        for match in po_regex.findall(content):
            traceability_map["proof_obligations"].append({"id": match, "file": rel_path})
        for match in conf_regex.findall(content):
            traceability_map["conformance_requirements"].append({"id": match, "file": rel_path})
        for match in adr_regex.findall(content):
            traceability_map["adrs"].append({"id": match, "file": rel_path})

    report_path = root_dir / "ops" / "reports" / "SPECIFICATION_TRACEABILITY.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(traceability_map, indent=2), encoding="utf-8")

    print(f"[✓] Traceability Compiled:")
    print(f"    -> Invariants        : {len(traceability_map['invariants'])}")
    print(f"    -> Proof Obligations : {len(traceability_map['proof_obligations'])}")
    print(f"    -> Conformance Reqs  : {len(traceability_map['conformance_requirements'])}")
    print(f"    -> ADR References    : {len(traceability_map['adrs'])}")
    print(f"    -> Output File       : {report_path}")

if __name__ == "__main__":
    main()
