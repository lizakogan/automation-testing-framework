"""Black-box CLI tests with console, JSON, and JUnit XML reports."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build import build


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sanitize", action="store_true")
    args = parser.parse_args()
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    cases = json.loads((ROOT / "tests" / "cases.json").read_text())
    started = time.perf_counter()
    results = []
    try:
        binary = build(args.sanitize)
    except (RuntimeError, OSError, subprocess.CalledProcessError) as exc:
        results.append(dict(name="build", category="infrastructure", passed=False,
                            duration_seconds=0, detail=str(exc)))
    else:
        for case in cases:
            start = time.perf_counter()
            detail = ""
            try:
                proc = subprocess.run([str(binary)], input=case["input"],
                                      capture_output=True, text=True, timeout=5)
                actual = [json.loads(line) for line in proc.stdout.splitlines()]
                problems = []
                if actual != case["expected"]:
                    problems.append(f"Expected: {case['expected']}\nActual: {actual}")
                if proc.returncode != case["exit_code"]:
                    problems.append(f"Expected exit {case['exit_code']}; got {proc.returncode}")
                if proc.stderr:
                    problems.append(f"Unexpected stderr: {proc.stderr}")
                detail = "\n".join(problems)
            except (OSError, subprocess.TimeoutExpired, ValueError) as exc:
                detail = f"{type(exc).__name__}: {exc}"
            result = dict(name=case["name"], category=case["category"],
                          passed=not detail, duration_seconds=time.perf_counter()-start,
                          detail=detail)
            results.append(result)
            print(f"{'PASS' if result['passed'] else 'FAIL'} {case['name']}")
            if detail:
                print(detail)
    failures = sum(not r["passed"] for r in results)
    duration = time.perf_counter() - started
    report = dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),
                  tests=len(results), failures=failures, duration_seconds=duration,
                  results=results)
    (reports / "results.json").write_text(json.dumps(report, indent=2) + "\n")
    suite = ET.Element("testsuite", name="account-cli", tests=str(len(results)),
                       failures=str(failures), time=f"{duration:.6f}")
    for result in results:
        node = ET.SubElement(suite, "testcase", name=result["name"],
                             classname=result["category"],
                             time=f"{result['duration_seconds']:.6f}")
        if not result["passed"]:
            ET.SubElement(node, "failure", message="Test failed").text = result["detail"]
    ET.indent(suite)
    ET.ElementTree(suite).write(reports / "junit.xml", encoding="utf-8", xml_declaration=True)
    print(f"\n{len(results)-failures}/{len(results)} passed; {failures} failed.")
    print(f"Reports: {reports}")
    return 1 if failures else 0

if __name__ == "__main__":
    sys.exit(main())
