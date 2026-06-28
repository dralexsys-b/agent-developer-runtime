#!/usr/bin/env bash
set -euo pipefail

# Standalone Verification Pipeline for agent-developer-runtime
# Usage: ./scripts/verify.sh [--fast]
#
# Exit codes:
#   0    All checks passed
#   1    Ruff failed
#   2    MyPy failed
#   3    Pytest failed
#   4    Smoke tests failed
#   64   Invalid arguments
#   126  Repository or configuration error
#   127  Required command not found

# Make script work from any directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT" || exit 126

FAST_MODE=false

# Parse arguments (before require_command so --help works on clean machines)
for arg in "$@"; do
    case "$arg" in
        --fast)
            FAST_MODE=true
            ;;
        --help|-h)
            printf 'Usage:\n'
            printf '    %s [--fast]\n' "$0"
            printf '\n'
            printf 'Runs:\n'
            printf '    Ruff\n'
            printf '    MyPy (unless --fast)\n'
            printf '    Pytest\n'
            printf '    Shell smoke tests (tests/scripts/test_*.sh)\n'
            printf '\n'
            printf 'Options:\n'
            printf '    --fast    Skip mypy (faster verification)\n'
            printf '\n'
            printf 'Environment:\n'
            printf '    VERIFY_SKIP_SMOKE=1    Skip shell smoke tests\n'
            exit 0
            ;;
        *)
            printf 'Unknown option: %s\n' "$arg"
            printf 'Use --help for usage information\n'
            exit 64
            ;;
    esac
done

# Check for required commands (after argument parsing)
require_command() {
    command -v "$1" >/dev/null 2>&1 || {
        printf 'Required command not found: %s\n' "$1"
        exit 127
    }
}

require_command git
require_command ruff
require_command pytest

# Only require mypy if not in fast mode
if [ "$FAST_MODE" = false ]; then
    require_command mypy
fi

# Verify we are in a Git repository
if ! git rev-parse --show-toplevel >/dev/null 2>&1; then
    printf 'Not inside a Git repository\n'
    exit 126
fi

# Verify repository root matches expected location
TOPLEVEL="$(git rev-parse --show-toplevel)"
if [ "$TOPLEVEL" != "$REPO_ROOT" ]; then
    printf 'Repository root mismatch\n'
    exit 126
fi

# Define commands as arrays for future extensibility
RUFF_CMD=(ruff check .)
MYPY_CMD=(mypy src)
PYTEST_CMD=(pytest -q)

# Run Ruff
printf '== Ruff ==\n'
if "${RUFF_CMD[@]}"; then
    printf 'PASS\n'
else
    printf 'FAIL\n'
    exit 1
fi
printf '\n'

# Run MyPy (unless fast mode)
if [ "$FAST_MODE" = false ]; then
    printf '== MyPy ==\n'
    if "${MYPY_CMD[@]}"; then
        printf 'PASS\n'
    else
        printf 'FAIL\n'
        exit 2
    fi
    printf '\n'
else
    printf '== MyPy ==\n'
    printf 'SKIPPED (fast mode)\n'
    printf '\n'
fi

# Run Pytest
printf '== Pytest ==\n'
if "${PYTEST_CMD[@]}"; then
    printf 'PASS\n'
else
    printf 'FAIL\n'
    exit 3
fi
printf '\n'

# Run shell smoke tests (unless VERIFY_SKIP_SMOKE is set)
if [ "${VERIFY_SKIP_SMOKE:-0}" != "1" ]; then
    printf '== Shell Smoke Tests ==\n'
    smoke_tests_failed=0
    
    # Use nullglob to handle case when no test files exist
    shopt -s nullglob
    test_files=(tests/scripts/test_*.sh)
    shopt -u nullglob
    
    if [ ${#test_files[@]} -eq 0 ]; then
        printf 'No shell smoke tests found\n'
    else
        for test_script in "${test_files[@]}"; do
            if [ -f "$test_script" ] && [ -x "$test_script" ]; then
                printf 'Running %s... ' "$(basename "$test_script")"
                
                # Run test and capture output
                tmp_log="$(mktemp)"
                if "$test_script" >"$tmp_log" 2>&1; then
                    printf 'PASS\n'
                    rm -f "$tmp_log"
                else
                    printf 'FAIL\n'
                    printf '\nSmoke test output:\n'
                    printf '----------------------------------------\n'
                    cat "$tmp_log"
                    printf '----------------------------------------\n'
                    rm -f "$tmp_log"
                    smoke_tests_failed=1
                fi
            fi
        done
    fi
    
    if [ "$smoke_tests_failed" -eq 1 ]; then
        exit 4
    fi
    
    printf '\n'
else
    printf '== Shell Smoke Tests ==\n'
    printf 'SKIPPED (VERIFY_SKIP_SMOKE=1)\n'
    printf '\n'
fi

printf 'Verification PASSED\n'
exit 0
