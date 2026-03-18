#!/usr/bin/env python
"""
Test Runner Script for Smart Voice Interviewer Backend

Provides convenient commands to run different test suites.
"""

import argparse
import subprocess
import sys


def run_command(cmd, description):
    """Run a command and print the description."""
    print(f"\n{'='*60}")
    print(f"  {description}")
    print(f"{'='*60}\n")
    
    result = subprocess.run(cmd, shell=True)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(
        description="Run tests for Smart Voice Interviewer backend"
    )
    
    parser.add_argument(
        "suite",
        nargs="?",
        default="all",
        choices=[
            "all", "unit", "integration", "database", 
            "auth", "interview", "profile", "general",
            "coverage", "quick", "slow"
        ],
        help="Test suite to run (default: all)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "-k", "--keyword",
        type=str,
        help="Run tests matching keyword"
    )
    
    parser.add_argument(
        "-f", "--file",
        type=str,
        help="Run specific test file"
    )
    
    parser.add_argument(
        "--pdb",
        action="store_true",
        help="Drop into debugger on failures"
    )
    
    parser.add_argument(
        "--lf",
        action="store_true",
        help="Run last failed tests"
    )
    
    args = parser.parse_args()
    
    # Build pytest command
    cmd_parts = ["pytest"]
    
    # Add test suite/marker
    if args.suite == "all":
        cmd_parts.append("tests/")
    elif args.suite == "coverage":
        cmd_parts.extend(["--cov", "--cov-report=html", "--cov-report=term-missing", "tests/"])
    elif args.suite == "quick":
        cmd_parts.extend(["-m", "not slow", "tests/"])
    elif args.suite in ["unit", "integration", "database", "auth", "interview", "profile"]:
        cmd_parts.extend(["-m", args.suite, "tests/"])
    elif args.suite == "general":
        cmd_parts.append("tests/test_general.py")
    elif args.suite == "slow":
        cmd_parts.extend(["-m", "slow", "tests/"])
    
    # Add file filter
    if args.file:
        cmd_parts = ["pytest", f"tests/{args.file}"]
    
    # Add keyword filter
    if args.keyword:
        cmd_parts.extend(["-k", args.keyword])
    
    # Add verbose flag
    if args.verbose:
        cmd_parts.append("-v")
    
    # Add debugger flag
    if args.pdb:
        cmd_parts.append("--pdb")
    
    # Add last failed flag
    if args.lf:
        cmd_parts.append("--lf")
    
    # Run the tests
    cmd = " ".join(cmd_parts)
    description = f"Running: {cmd}"
    
    exit_code = run_command(cmd, description)
    
    # Print summary
    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed.")
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
