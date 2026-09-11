"""Command-line entry point: python -m agent <command>."""

from __future__ import annotations

import argparse

from .orchestrator import generate, show_plan, verify


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate and replay the EducationPals course.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("verify", help="Run offline repository and artifact checks.")
    subparsers.add_parser("show-plan", help="Print the cached foundations without writing lessons.")
    generate_parser = subparsers.add_parser("generate", help="Generate all course artifacts.")
    generate_parser.add_argument(
        "--offline",
        action="store_true",
        help="Replay exact cached responses and make no network calls.",
    )
    args = parser.parse_args()
    if args.command == "verify":
        verify()
    elif args.command == "show-plan":
        show_plan()
    elif args.command == "generate":
        generate(offline=args.offline)


if __name__ == "__main__":
    main()
