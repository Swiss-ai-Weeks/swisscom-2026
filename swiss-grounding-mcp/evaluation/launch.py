#!/usr/bin/env python3
"""Run the versioned session utility without restoring working-tree files."""

from pathlib import Path
import subprocess
import sys
import tempfile
import time


SNAPSHOT = sys.argv[1]
PREFIX = "swiss-grounding-mcp/evaluation"
ROOT = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip())
FILES = (
    "README.md", "display.py", "reference-note.txt", "sample-questions.b64",
    "sample_runner.py", "session.md", "test_sample_runner.py", "test_display.py",
)


def materialize(directory):
    for name in FILES:
        result = subprocess.run(
            ["git", "show", f"{SNAPSHOT}:{PREFIX}/{name}"],
            cwd=ROOT, check=True, capture_output=True, timeout=10,
        )
        (directory / name).write_bytes(result.stdout)


def main(argv=None):
    args = list(sys.argv[2:] if argv is None else argv)
    try:
        with tempfile.TemporaryDirectory(prefix="swiss-session-") as temporary:
            directory = Path(temporary)
            materialize(directory)
            if args == ["--check"]:
                command = [sys.executable, "-B", "-m", "unittest", "discover",
                           "-s", str(directory), "-p", "test_*.py"]
            else:
                command = [sys.executable, "-B", str(directory / "sample_runner.py"), *args]
            result = subprocess.run(command, timeout=150)
            if result.returncode == 0 and not any(
                option in args for option in ("--check", "--dry-run", "--help", "-h")
            ):
                # Detached terminals need the files until their bounded run ends.
                time.sleep(10)
            return result.returncode
    except (OSError, subprocess.SubprocessError) as error:
        print(f"Session utility unavailable ({type(error).__name__}). "
              f"Requires Git and snapshot {SNAPSHOT}; shallow clones may need "
              "`git fetch --unshallow`. Continue with the task.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
