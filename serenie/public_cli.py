import sys
import os
import json
import time
import hashlib
import argparse
from dataclasses import dataclass
from typing import Dict, List, Any, Tuple, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from runtime.serialization.ceap_validator import CEAPConformanceValidator
from runtime.dtr.serenie_substrate import IdentityEngine, EvidenceJournalLedger, EvidenceFact


class SerenieCLI:
    def __init__(self):
        self.identity = IdentityEngine()
        self.ledger = EvidenceJournalLedger()

    def run(self, argv: List[str]) -> int:
        parser = argparse.ArgumentParser(
            description="Serenie Substrate Command Line Interface v0.1.0",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        subparsers = parser.add_subparsers(dest="command", required=True)

        ingest_p = subparsers.add_parser("ingest", help="Compile and append an engineering artifact to the ledger.")
        ingest_p.add_argument("--file", required=True, help="Path to target project code or specification file.")

        subparsers.add_parser("verify", help="Run cryptographic hash-chain validations over the ledger records.")
        subparsers.add_parser("export", help="Output the continuous immutable transaction chain as JSON.")

        args = parser.parse_args(argv)

        try:
            if args.command == "ingest":
                return self._execute_ingest(args.file)
            elif args.command == "verify":
                return self._execute_verify()
            elif args.command == "export":
                return self._execute_export()
        except Exception as e:
            print(f"[FATAL] Engine Invariant Failure: {str(e)}", file=sys.stderr)
            return 1
        return 0

    def _execute_ingest(self, file_path: str) -> int:
        if not os.path.exists(file_path):
            print(f"[ERROR] File not found: '{file_path}'", file=sys.stderr)
            return 1

        with open(file_path, "r", encoding="utf-8") as f:
            raw_content = f.read()

        for marker in ["TODO", "FIXME", "XXX"]:
            if marker in raw_content:
                print(f"[REJECTED] Code placeholder token '{marker}' blocked by system rules.", file=sys.stderr)
                return 1

        print(f"[*] Compiling file target: '{file_path}'...")
        validator = CEAPConformanceValidator(raw_content, "ART-001", "REV-01")
        envelope, success = validator.compile_to_envelope(file_path, "serenie.runtime")

        if not success:
            print(f"[REJECTED] CEAP Compilation failed: {envelope.get('error')}", file=sys.stderr)
            return 1

        coord = self.identity.derive_coordinate("ART-001", "REV-01", envelope)

        fact = EvidenceFact(
            evidence_id=f"EVID-{coord.content_hash[:16].upper()}",
            contract_name="CEAP_Ingest_Gate",
            determinism_level="D_4",
            input_coordinate=f"RAW::{file_path}",
            output_coordinate=coord.to_coordinate_string(),
            monotonic_step=0,
            latency_seconds=0.001
        )

        block_hash = self.ledger.commit_fact(fact, coord.content_hash)
        print("[✓] Artifact committed to evidence ledger.")
        print(f"    -> Identity : {coord.to_coordinate_string()}")
        print(f"    -> Block Signature : {block_hash}")
        return 0

    def _execute_verify(self) -> int:
        print("[*] Running ledger hash chain verification...")
        is_valid = self.ledger.verify_journal_provability()
        if is_valid:
            print("[✓] Verification Complete: Ledger hash chain is unbroken.")
            return 0
        else:
            print("[ERROR] Cryptographic modification detected in evidence journal!", file=sys.stderr)
            return 1

    def _execute_export(self) -> int:
        print(json.dumps(self.ledger._timeline, indent=2))
        return 0


def main(argv: Optional[List[str]] = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    return SerenieCLI().run(argv)


if __name__ == "__main__":
    raise SystemExit(main())
