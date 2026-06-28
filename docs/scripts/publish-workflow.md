# Publish Workflow Specification

## Purpose

Automates the complete workflow for publishing changes to the
agent-developer-runtime repository, including staging, verification,
commit creation, and synchronization with origin.

## CLI Interface

    ./scripts/publish.sh [options]

Options:
    -F FILE       Read commit message from FILE
    -m TEXT       Use TEXT as commit message
    --fast        Skip mypy during verification
    --dry-run     Preview actions without modifying the repository
    --help        Show usage information

## Preconditions

- Repository exists
- Current branch is a publishable branch
- Repository is in a publishable state
- Commit message is available (via -F or -m)
- Origin remote exists
- Network access to origin

## Exit Codes

    0    Successfully published
    1    Verification failed (ruff/mypy/pytest)
    2    Nothing staged to commit
    3    Staging failed
    4    Commit creation failed
    5    Push failed
    6    Remote synchronization failed
    126  Repository or configuration error
    127  Required command not found

## Sequence of Actions

1. Verify repository (repository exists, publishable branch)
2. Stage repository changes
3. Ensure there is something staged (git diff --cached --quiet)
4. Run verification against the current repository state
5. Create commit with provided message
6. Verify commit contents (git show --stat HEAD)
7. Push to origin
8. Fetch from origin
9. Compare local HEAD with origin
10. Print summary

## Postconditions

- Working tree is clean
- Local HEAD equals origin HEAD
- Verification completed successfully
- All changes published to remote

## Guarantees

- Verification pipeline completes successfully before commit creation
- Working directory is clean before staging
- Commit message is valid before commit creation
- Successful publish operations synchronize the local branch with origin
- Each step has distinct exit code for debugging

## Does NOT Do

- Merge branches
- Resolve conflicts
- Edit commit messages
- Create tags or releases
- Update CHANGELOG
- Bump version numbers
- Create GitHub releases
- Modify source code
- Handle network failure gracefully (fails fast)

## Dependencies

Requires:
- ./scripts/verify.sh (verification pipeline)
- git (version control)

Network access is required only for push and remote verification.

## Usage Examples

Standard publish with file:

    cat > /tmp/commit-msg.txt << 'MSG'
    feat(domain): add new aggregate

    Adds Customer aggregate with basic operations.

    Verification:
    - Ruff ✓
    - MyPy ✓
    - Pytest ✓
    MSG

    ./scripts/publish.sh -F /tmp/commit-msg.txt

Quick publish with inline message:

    ./scripts/publish.sh -m "docs: update README"

Fast publish (skip mypy):

    ./scripts/publish.sh -F /tmp/commit-msg.txt --fast

Dry run (preview only):

    ./scripts/publish.sh -F /tmp/commit-msg.txt --dry-run

## Relationship to verify.sh

publish.sh uses verify.sh as its verification step.
verify.sh remains usable standalone.
Both scripts follow the same CLI conventions.
Both scripts are independent tools.
