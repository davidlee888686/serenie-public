import argparse
from runtime.runtime_engine import SerenieRuntimeEngine

def main():
    parser = argparse.ArgumentParser(description='Serenie Runtime')
    sub = parser.add_subparsers(dest='cmd')

    p = sub.add_parser('ingest')
    p.add_argument('--input', required=True)
    p.add_argument('--logical-id', required=True)
    p.add_argument('--version-id', type=int, required=True)

    p = sub.add_parser('delta')
    p.add_argument('--before', required=True)
    p.add_argument('--after', required=True)

    p = sub.add_parser('replay')

    p = sub.add_parser('project')

    p = sub.add_parser('save')
    p.add_argument('--output', required=True)

    p = sub.add_parser('load')
    p.add_argument('--input', required=True)

    args = parser.parse_args()
    engine = SerenieRuntimeEngine()

    if args.cmd == 'ingest':
        engine.ingest(args.input, args.logical_id, args.version_id)
    elif args.cmd == 'delta':
        engine.delta(args.before, args.after)
    elif args.cmd == 'replay':
        engine.replay()
    elif args.cmd == 'project':
        engine.project()
    elif args.cmd == 'save':
        engine.save_state(args.output)
    elif args.cmd == 'load':
        engine.load_state(args.input)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
