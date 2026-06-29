#!/usr/bin/env bash
set -euo pipefail

# Smoke tests for scripts/publish.sh
# Tests user workflows using isolated temporary repositories.
#
# Exit codes:
#   0    All tests passed
#   1    One or more tests failed

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PUBLISH_SH="$REPO_ROOT/scripts/publish.sh"

TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

run_test() {
    local name="$1"
    local expected_exit="$2"
    shift 2
    local cmd=("$@")
    TESTS_RUN=$((TESTS_RUN + 1))
    local actual_exit=0
    "${cmd[@]}" >/dev/null 2>&1 || actual_exit=$?
    if [ "$actual_exit" -eq "$expected_exit" ]; then
        printf 'PASS  %s\n' "$name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        printf 'FAIL  %s (expected %d, got %d)\n' "$name" "$expected_exit" "$actual_exit"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

run_test_output_contains() {
    local name="$1"
    local expected_text="$2"
    shift 2
    local cmd=("$@")
    TESTS_RUN=$((TESTS_RUN + 1))
    local output
    output=$("${cmd[@]}" 2>&1) || true
    if printf '%s' "$output" | grep -Fq "$expected_text"; then
        printf 'PASS  %s\n' "$name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        printf 'FAIL  %s (output missing "%s")\n' "$name" "$expected_text"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

setup_temp_repo() {
    local repo
    local origin_root
    local origin
    repo="$(mktemp -d)"
    origin_root="$(mktemp -d)"
    origin="$origin_root/origin.git"
    (
        cd "$repo"
        git init -q
        git config user.email "test@test.com"
        git config user.name "Test"
        mkdir -p scripts
        cp "$PUBLISH_SH" scripts/
        chmod +x scripts/publish.sh
        cat > scripts/verify.sh << 'STUB_EOF'
#!/usr/bin/env bash
exit 0
STUB_EOF
        chmod +x scripts/verify.sh
        mkdir -p src
        echo "# empty" > src/__init__.py
        git add -A
        git commit -q -m "initial"
        git init --bare -q "$origin"
        git remote add origin "$origin"
        CURRENT_BRANCH="$(git symbolic-ref --short HEAD)"
        git push -u origin "$CURRENT_BRANCH" >/dev/null 2>&1
    )
    printf '%s\t%s\n' "$repo" "$origin_root"
}

cleanup_temp_repo() {
    local repo="$1"
    local origin_root="$2"
    rm -rf "$repo" "$origin_root"
}

printf '== publish.sh smoke tests ==\n\n'
printf '=== CLI Tests ===\n'

run_test "--help returns 0" 0 "$PUBLISH_SH" --help
run_test "-h returns 0" 0 "$PUBLISH_SH" -h
run_test_output_contains "--help mentions Usage" "Usage:" "$PUBLISH_SH" --help
run_test_output_contains "--help mentions Exit codes" "Exit codes:" "$PUBLISH_SH" --help
run_test "no commit message returns 64" 64 "$PUBLISH_SH"
run_test "unknown argument returns 64" 64 "$PUBLISH_SH" --unknown-flag

TMPFILE_MISSING="$(mktemp)"
rm "$TMPFILE_MISSING"
run_test "-F with missing file returns 64" 64 "$PUBLISH_SH" -F "$TMPFILE_MISSING"

TMPFILE_MSG="$(mktemp)"
echo "test" > "$TMPFILE_MSG"
run_test "both -F and -m returns 64" 64 "$PUBLISH_SH" -F "$TMPFILE_MSG" -m "test"
rm -f "$TMPFILE_MSG"

printf '\n=== Workflow Tests ===\n'

paths="$(setup_temp_repo)"
IFS=$'\t' read -r TMPDIR_CLEAN TMPDIR_CLEAN_ORIGIN <<<"$paths"
run_test "--dry-run on clean repo returns 2" 2 \
    bash -c "cd '$TMPDIR_CLEAN' && ./scripts/publish.sh --dry-run -m 'test'"
cleanup_temp_repo "$TMPDIR_CLEAN" "$TMPDIR_CLEAN_ORIGIN"

paths="$(setup_temp_repo)"
IFS=$'\t' read -r TMPDIR_UNTRACKED TMPDIR_UNTRACKED_ORIGIN <<<"$paths"
echo "# test" > "$TMPDIR_UNTRACKED/test.txt"
run_test "--dry-run with untracked file returns 0" 0 \
    bash -c "cd '$TMPDIR_UNTRACKED' && ./scripts/publish.sh --dry-run -m 'test'"
cleanup_temp_repo "$TMPDIR_UNTRACKED" "$TMPDIR_UNTRACKED_ORIGIN"

paths="$(setup_temp_repo)"
IFS=$'\t' read -r TMPDIR_FAST TMPDIR_FAST_ORIGIN <<<"$paths"
echo "# test" > "$TMPDIR_FAST/test.txt"
run_test "--fast flag accepted in dry-run" 0 \
    bash -c "cd '$TMPDIR_FAST' && ./scripts/publish.sh --dry-run --fast -m 'test'"
cleanup_temp_repo "$TMPDIR_FAST" "$TMPDIR_FAST_ORIGIN"

paths="$(setup_temp_repo)"
IFS=$'\t' read -r TMPDIR_ANY_DIR TMPDIR_ANY_DIR_ORIGIN <<<"$paths"
echo "# test" > "$TMPDIR_ANY_DIR/test.txt"
run_test "publish.sh works from different directory" 0 \
    bash -c "cd /tmp && '$TMPDIR_ANY_DIR/scripts/publish.sh' --dry-run -m 'test'"
cleanup_temp_repo "$TMPDIR_ANY_DIR" "$TMPDIR_ANY_DIR_ORIGIN"

printf '\n=== Safety Tests ===\n'

paths="$(setup_temp_repo)"
IFS=$'\t' read -r TMPDIR_NO_EFFECTS TMPDIR_NO_EFFECTS_ORIGIN <<<"$paths"
echo "# test" > "$TMPDIR_NO_EFFECTS/test.txt"
before_status="$(cd "$TMPDIR_NO_EFFECTS" && git status --porcelain=v1)"
(cd "$TMPDIR_NO_EFFECTS" && ./scripts/publish.sh --dry-run -m "test" >/dev/null 2>&1) || true
after_status="$(cd "$TMPDIR_NO_EFFECTS" && git status --porcelain=v1)"
TESTS_RUN=$((TESTS_RUN + 1))
if [ "$before_status" = "$after_status" ]; then
    printf 'PASS  --dry-run shows no side effects\n'
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    printf 'FAIL  --dry-run shows no side effects (repository state changed)\n'
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
cleanup_temp_repo "$TMPDIR_NO_EFFECTS" "$TMPDIR_NO_EFFECTS_ORIGIN"

paths="$(setup_temp_repo)"
IFS=$'\t' read -r TMPDIR_NO_VERIFY TMPDIR_NO_VERIFY_ORIGIN <<<"$paths"
rm -f "$TMPDIR_NO_VERIFY/scripts/verify.sh"
run_test "missing verify.sh returns 126" 126 \
    bash -c "cd '$TMPDIR_NO_VERIFY' && ./scripts/publish.sh --dry-run -m 'test'"
cleanup_temp_repo "$TMPDIR_NO_VERIFY" "$TMPDIR_NO_VERIFY_ORIGIN"

paths="$(setup_temp_repo)"
IFS=$'\t' read -r TMPDIR_VERIFY_INTEGRATION TMPDIR_VERIFY_INTEGRATION_ORIGIN <<<"$paths"
echo "# test" > "$TMPDIR_VERIFY_INTEGRATION/test.txt"
cat > "$TMPDIR_VERIFY_INTEGRATION/scripts/verify.sh" << 'INNER_EOF'
#!/usr/bin/env bash
exit 1
INNER_EOF
chmod +x "$TMPDIR_VERIFY_INTEGRATION/scripts/verify.sh"
run_test "publish.sh fails when verify.sh fails" 1 \
    bash -c "cd '$TMPDIR_VERIFY_INTEGRATION' && ./scripts/publish.sh --dry-run -m 'test'"
cleanup_temp_repo "$TMPDIR_VERIFY_INTEGRATION" "$TMPDIR_VERIFY_INTEGRATION_ORIGIN"

printf '\n== Summary ==\n'
printf 'Tests run:    %d\n' "$TESTS_RUN"
printf 'Tests passed: %d\n' "$TESTS_PASSED"
printf 'Tests failed: %d\n' "$TESTS_FAILED"

if [ "$TESTS_FAILED" -gt 0 ]; then
    exit 1
fi
exit 0
