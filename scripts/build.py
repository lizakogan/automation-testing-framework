"""Build with a local C compiler; no third-party Python packages required."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BINARY = ROOT / "build" / ("account.exe" if os.name == "nt" else "account")

def build(sanitize=False):
    compiler = os.environ.get("CC") or shutil.which("clang") or shutil.which("gcc")
    if not compiler:
        raise RuntimeError("Install clang or gcc and put it on PATH. See README.md.")
    BINARY.parent.mkdir(exist_ok=True)
    command = [compiler, "-std=c11", "-Wall", "-Wextra", "-Wpedantic", "-Werror", "-g"]
    if sanitize:
        command += ["-fsanitize=address,undefined", "-fno-omit-frame-pointer"]
    command += [str(ROOT / "src" / "account.c"), "-o", str(BINARY)]
    subprocess.run(command, check=True)
    print(f"Built {BINARY}")
    return BINARY

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sanitize", action="store_true")
    args = parser.parse_args()
    try:
        build(args.sanitize)
    except (RuntimeError, OSError, subprocess.CalledProcessError) as exc:
        print(f"Build failed: {exc}", file=sys.stderr)
        sys.exit(2)
