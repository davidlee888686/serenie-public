"""Allow `python -m serenie` to run the public CLI."""

from serenie.public_cli import main

if __name__ == "__main__":
    raise SystemExit(main())
