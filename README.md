# Automation Testing Framework

A C command-line account application with automated Python tests and a GitHub
Actions workflow. The tests cover normal transactions, invalid input, boundary
values, and balance preservation after failed operations.

## Requirements

- Python 3.10 or newer
- GCC or Clang with C11 support, available on PATH

The Python scripts use only the standard library. Run the commands below from
the project root, where this README is located.

## Build

```sh
python3 scripts/build.py
```

This creates `build/account` on macOS/Linux or `build/account.exe` on Windows.
The script uses Clang if available, otherwise GCC. Set `CC` to select a compiler.

## Run the application

On macOS/Linux:

```sh
./build/account
```

Enter one command per line:

```text
deposit 1250
withdraw 250
balance
```

Amounts are positive integer cents: `1250` represents `12.50`. The example produces:

```json
{"status":"ok","code":"deposit","balance_cents":1250}
{"status":"ok","code":"withdraw","balance_cents":1000}
{"status":"ok","code":"balance","balance_cents":1000}
```

Supported commands are `deposit <amount>`, `withdraw <amount>`, and `balance`.
Invalid commands return an error without changing the balance. Processing
continues after an error. Each run starts at zero; balances are not saved.

End input with Ctrl+D on macOS/Linux. On Windows, run `.\build\account.exe`
and end input with Ctrl+Z followed by Enter. Use `python` instead of `python3`
for the Python commands if that is how Python is installed on your Windows system.

## Run the tests

```sh
python3 tests/run_tests.py
```

The runner builds the application automatically and runs each test in a separate
process. It checks JSON output, exit codes, and unexpected stderr against the
fixtures in `tests/cases.json`. Each test has a five-second timeout.

To enable AddressSanitizer and UndefinedBehaviorSanitizer on a supported platform:

```sh
python3 tests/run_tests.py --sanitize
```

Reports are written to:

- `reports/results.json` — totals and individual test results
- `reports/junit.xml` — JUnit-compatible results

The test runner returns `0` when all tests pass and `1` when a test or build fails.
An expected application error counts as a passing test when it matches the fixture.

## VS Code

Open this folder in VS Code and use **Terminal > New Terminal** to run the commands.
The included tasks are also available under **Terminal > Run Task**:

- **Build C application**
- **Run automated tests**

## Continuous integration

The GitHub Actions workflow runs the tests on Ubuntu with both GCC and Clang,
with sanitizers enabled. It runs on pushes and pull requests and supports manual
execution. Test reports are uploaded as artifacts, including when tests fail.
Check the repository's **Actions** tab for results after pushing to GitHub.

## Files

| Path | Purpose |
| --- | --- |
| `src/account.c` | Application |
| `scripts/build.py` | Build script |
| `tests/cases.json` | Test inputs and expected results |
| `tests/run_tests.py` | Test runner and report generation |
| `.github/workflows/ci.yml` | CI workflow |
| `.vscode/` | VS Code tasks and extension suggestions |

Generated files in `build/` and `reports/` are excluded from Git.