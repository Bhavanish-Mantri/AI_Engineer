"""Convenience entrypoint so `uv run main.py ...` works like `ytrag ...`."""

from ytrag.cli import app


def main():
    app()


if __name__ == "__main__":
    main()
