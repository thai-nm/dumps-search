#!/usr/bin/env python3
"""
CLI module for dumps-search tool.
Provides command-line interface for searching ExamTopics questions and generating PDFs.
"""

import argparse
import sys
from typing import Optional

from . import __version__


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="dumps-search",
        description="Search for questions/answers of a specific topic on Exam Topics and save them as PDF files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  dumps-search "AWS Solutions Architect" 1 50
  dumps-search "Azure Fundamentals" 10 25
  dumps-search "CompTIA Security+" 1 100

For more information, visit: https://github.com/thai-nm/dumps-search
        """,
    )

    parser.add_argument(
        "keyword",
        type=str,
        help="The keyword to search for the topic on Exam Topics",
    )

    parser.add_argument(
        "start",
        type=int,
        help="The start number of question (inclusive)",
    )

    parser.add_argument(
        "end",
        type=int,
        help="The end number of question (inclusive)",
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="output.pdf",
        help="Output PDF filename (default: output.pdf)",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually doing it",
    )

    return parser


def validate_arguments(args: argparse.Namespace) -> bool:
    """Validate the parsed arguments."""
    if args.start < 1:
        print("Error: Start number must be greater than 0", file=sys.stderr)
        return False

    if args.end < args.start:
        print("Error: End number must be greater than or equal to start number", file=sys.stderr)
        return False

    if args.end - args.start > 1000:
        print("Warning: Large range detected. This might take a long time.", file=sys.stderr)
        response = input("Do you want to continue? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            return False

    return True


def main(argv: Optional[list] = None) -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args(argv)

    # Validate arguments
    if not validate_arguments(args):
        return 1

    # Print configuration
    if args.verbose or args.dry_run:
        print(f"dumps-search v{__version__}")
        print(f"Keyword: {args.keyword}")
        print(f"Question range: {args.start} to {args.end}")
        print(f"Output file: {args.output}")
        print(f"Total questions: {args.end - args.start + 1}")
        print()

    if args.dry_run:
        print("Dry run mode - no actual operations will be performed")
        print("Would search for ExamTopics URLs and generate PDF...")
        return 0

    # TODO: Implement actual functionality in future phases
    print("Phase 1 implementation - CLI structure ready!")
    print(f"Searching for '{args.keyword}' questions {args.start}-{args.end}")
    print(f"Output will be saved to: {args.output}")
    print("\nNote: Search and PDF generation functionality will be implemented in Phase 2 and 3.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
