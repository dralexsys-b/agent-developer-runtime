#!/usr/bin/env bash
set -euo pipefail

# Publish workflow automation for agent-developer-runtime
# Usage: ./scripts/publish.sh [options]
#
# Exit codes:
#   0    Successfully published
#   1    Verification failed (ruff/mypy/pytest)
#   2    No changes to publish
#   3    Staging failed
#   4    Commit creation failed
#   5    Push failed
#   6    Remote synchronization failed
#   64   Invalid arguments
#   126  Repository or configuration error
#   127  Required command not found

# Make script work from any directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT" || exit 126

# Parse arguments before require_command so --help works on clean machines
COMMIT_MSG_FILE=""
COMMIT_MSG_TEXT=""
FAST_MODE=false
DRY_RUN=false

while [ $# -gt 0 ]; do
    case "$1" in
        -F)
            shift
            if [ $# -eq 0 ]; then
                printf 'Error: -F requires a file argument\n'
                exit 64
            fi
            COMMIT_MSG_FILE="$1"
            shift
            ;;
        -m)
            shift
            if [ $# -eq 0 ]; then
                printf 'Error: -m requires a text argument\n'
                exit 64
            fi
            COMMIT_MSG_TEXT="$1"
            shift
            ;;
        --fast)
            FAST_MODE=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help|-h)
            printf 'Usage:\n'
            printf '    %s [options]\n' "$0"
            printf '\n'
            printf 'Options:\n'
            printf '    -F FILE       Read commit message from FILE\n'
            printf '    -m TEXT       Use TEXT as commit message\n'
            printf '    --fast        Skip mypy during verification\n'
            printf '    --dry-run     Preview actions without modifying the repository\n'
            printf '    --help        Show this help message\n'
            printf '\n'
            printf 'Exit codes:\n'
            printf '    0    Successfully published\n'
            printf '    1    Verification failed\n'
            printf '    2    No changes to publish\n'
            printf '    3    Staging failed\n'
            printf '    4    Commit creation failed\n'
            printf '    5    Push failed\n'
            printf '    6    Remote synchronization failed\n'
            printf '    64   Invalid arguments\n'
            printf '    126  Repository or configuration error\n'
            printf '    127  Required command not found\n'
            exit 0
            ;;
        *)
            printf 'Unknown option: %s\n' "$1"
            printf 'Use --help for usage information\n'
            exit 64
            ;;
    esac
done

# Check for required commands
require_command() {
    command -v "$1" >/dev/null 2>&1 || {
        printf 'Required command not found: %s\n' "$1"
        exit 127
    }
}

require_command git

# Verify verify.sh exists and is executable
if [ ! -x "$SCRIPT_DIR/verify.sh" ]; then
    printf 'Error: verify.sh is missing or not executable\n'
    exit 126
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

# Verify origin remote exists
if ! git remote get-url origin >/dev/null 2>&1; then
    printf 'Error: origin remote not found\n'
    exit 126
fi

# Verify we have a commit message
if [ -z "$COMMIT_MSG_FILE" ] && [ -z "$COMMIT_MSG_TEXT" ]; then
    printf 'Error: commit message required (use -F FILE or -m TEXT)\n'
    exit 64
fi

if [ -n "$COMMIT_MSG_FILE" ] && [ -n "$COMMIT_MSG_TEXT" ]; then
    printf 'Error: cannot use both -F and -m simultaneously\n'
    exit 64
fi

if [ -n "$COMMIT_MSG_FILE" ] && [ ! -r "$COMMIT_MSG_FILE" ]; then
    printf 'Error: commit message file not readable: %s\n' "$COMMIT_MSG_FILE"
    exit 64
fi

# Get current branch
CURRENT_BRANCH="$(git symbolic-ref --short HEAD 2>/dev/null || true)"
if [ -z "$CURRENT_BRANCH" ]; then
    printf 'Error: detached HEAD state, cannot publish\n'
    exit 126
fi

printf '== Publish Workflow ==\n'
printf 'Repository: %s\n' "$REPO_ROOT"
printf 'Branch: %s\n' "$CURRENT_BRANCH"
if [ "$DRY_RUN" = true ]; then
    printf 'Mode: DRY RUN (performs verification but skips repository modifications)\n'
fi
printf '\n'

# Step 1: Check if there are changes to publish
printf '== Step 1: Check Changes ==\n'
status="$(git status --porcelain=v1)" || exit 126
if [ -z "$status" ]; then
    printf 'No changes to publish\n'
    exit 2
fi
printf 'Repository has changes to publish\n'
git status --short
printf '\n'

# Step 2: Run verification pipeline (using absolute path)
printf '== Step 2: Run Verification Pipeline ==\n'
VERIFY_ARGS=()
if [ "$FAST_MODE" = true ]; then
    VERIFY_ARGS+=(--fast)
fi

if ! "$SCRIPT_DIR/verify.sh" "${VERIFY_ARGS[@]}"; then
    printf '\nVerification failed, aborting publish\n'
    exit 1
fi
printf '\n'

# Step 3: Handle dry-run (no side effects)
if [ "$DRY_RUN" = true ]; then
    printf '== Dry Run Summary ==\n'
    printf 'Would stage changes:\n'
    git status --short
    printf '\n'
    printf 'Would commit with message:\n'
    if [ -n "$COMMIT_MSG_FILE" ]; then
        cat "$COMMIT_MSG_FILE"
    else
        printf '%s\n' "$COMMIT_MSG_TEXT"
    fi
    printf '\n'
    printf 'Would push to origin/%s\n' "$CURRENT_BRANCH"
    printf '\n'
    printf 'Dry run completed successfully (verification passed, no repository modifications made)\n'
    exit 0
fi

# Step 4: Stage changes
printf '== Step 4: Stage Changes ==\n'
printf 'Changes after verification:\n'
git status --short
printf '\n'

if ! git add -A; then
    printf 'Staging failed\n'
    exit 3
fi

# Ensure there is something staged
if git diff --cached --quiet; then
    printf 'Nothing staged after git add -A\n'
    exit 2
fi

printf 'Changes staged:\n'
git diff --cached --stat
printf '\n'

# Step 5: Create commit (using command array)
printf '== Step 5: Create Commit ==\n'
COMMIT_CMD=(git commit)
if [ -n "$COMMIT_MSG_FILE" ]; then
    COMMIT_CMD+=(-F "$COMMIT_MSG_FILE")
else
    COMMIT_CMD+=(-m "$COMMIT_MSG_TEXT")
fi

if ! "${COMMIT_CMD[@]}"; then
    printf 'Commit creation failed\n'
    exit 4
fi

printf 'Commit created\n'
git log --oneline -1
printf '\n'

# Step 6: Verify commit contents
printf '== Step 6: Verify Commit Contents ==\n'
git show --stat --summary HEAD
printf '\n'

# Step 7: Push to origin
printf '== Step 7: Push to Origin ==\n'
if ! git push origin "$CURRENT_BRANCH"; then
    printf 'Push failed\n'
    exit 5
fi
printf '\n'

# Step 8: Fetch from origin
printf '== Step 8: Fetch from Origin ==\n'
if ! git fetch origin; then
    printf 'Fetch failed\n'
    exit 6
fi
printf '\n'

# Step 9: Compare local HEAD with origin
printf '== Step 9: Verify Remote Synchronization ==\n'
LOCAL_HEAD="$(git rev-parse HEAD)"
REMOTE_HEAD="$(git rev-parse "origin/$CURRENT_BRANCH")"

if [ "$LOCAL_HEAD" != "$REMOTE_HEAD" ]; then
    printf 'Error: local HEAD does not match origin/%s\n' "$CURRENT_BRANCH"
    printf 'Local:  %s\n' "$LOCAL_HEAD"
    printf 'Remote: %s\n' "$REMOTE_HEAD"
    exit 6
fi

printf 'Local HEAD synchronized with origin/%s\n' "$CURRENT_BRANCH"
printf '\n'

# Summary
printf '== Summary ==\n'
printf 'Successfully published to origin/%s\n' "$CURRENT_BRANCH"
printf 'Commit: %s\n' "$LOCAL_HEAD"
exit 0
