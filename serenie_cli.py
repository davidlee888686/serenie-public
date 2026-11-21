"""Source-tree entry point. The installable command is `serenie`."""

from serenie.public_cli import SerenieCLI, main

if __name__ == "__main__":
    raise SystemExit(main())
