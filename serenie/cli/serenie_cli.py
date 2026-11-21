import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from kernel.canonicalizer import Canonicalizer
from kernel.identity import compute_identity
from kernel.delta import DeltaEngine
from kernel.evidence import create_evidence
from kernel.journal import KernelJournal
from kernel.replay import KernelReplayEngine
from kernel.projection import KernelProjectionEngine

def cmd_canonicalize(args):
    data = Path(args.input).read_bytes()
    canon = Canonicalizer().canonicalize(data)
    if args.output:
        Path(args.output).write_bytes(canon)
    else:
        print(canon.decode('utf-8'))

def cmd_identity(args):
    data = Path(args.input).read_bytes()
    ident = compute_identity(args.logical_id, args.version_id, data)
    print(ident.to_string())

def cmd_delta(args):
    before = json.loads(Path(args.before).read_text())
    after = json.loads(Path(args.after).read_text())
    result = DeltaEngine().compare(before, after)
    print(json.dumps(result.__dict__, indent=2))

def cmd_evidence(args):
    record = create_evidence(args.logical_id, args.version_id, args.content_hash, {})
    print(json.dumps(record.__dict__, indent=2))

def cmd_journal(args):
    journal = KernelJournal()
    entry = journal.append(args.event_type, {"payload": args.payload})
    print(json.dumps(entry.__dict__, indent=2))

def cmd_replay(args):
    entries = json.loads(Path(args.input).read_text())
    result = KernelReplayEngine().replay_journal_sequence(entries)
    print(json.dumps(result, indent=2))

def cmd_project(args):
    canonical = json.loads(Path(args.canonical).read_text())
    journal = json.loads(Path(args.journal).read_text())
    views = KernelProjectionEngine().build_projection_views(canonical, journal)
    print(json.dumps(views, indent=2))

def build_parser():
    parser = argparse.ArgumentParser(description='Serenie CLI')
    sub = parser.add_subparsers(dest='command')

    p = sub.add_parser('canonicalize')
    p.add_argument('--input', required=True)
    p.add_argument('--output')
    p.set_defaults(func=cmd_canonicalize)

    p = sub.add_parser('identity')
    p.add_argument('--input', required=True)
    p.add_argument('--logical-id', required=True)
    p.add_argument('--version-id', type=int, required=True)
    p.set_defaults(func=cmd_identity)

    p = sub.add_parser('delta')
    p.add_argument('--before', required=True)
    p.add_argument('--after', required=True)
    p.set_defaults(func=cmd_delta)

    p = sub.add_parser('evidence')
    p.add_argument('--logical-id', required=True)
    p.add_argument('--version-id', type=int, required=True)
    p.add_argument('--content-hash', required=True)
    p.set_defaults(func=cmd_evidence)

    p = sub.add_parser('journal')
    p.add_argument('--event-type', required=True)
    p.add_argument('--payload', required=True)
    p.set_defaults(func=cmd_journal)

    p = sub.add_parser('replay')
    p.add_argument('--input', required=True)
    p.set_defaults(func=cmd_replay)

    p = sub.add_parser('project')
    p.add_argument('--canonical', required=True)
    p.add_argument('--journal', required=True)
    p.set_defaults(func=cmd_project)

    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
