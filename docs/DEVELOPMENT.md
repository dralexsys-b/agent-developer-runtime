# Development Process

Engineering practices used throughout the Agent Developer project.

## Development Workflow

Every change follows this sequence:

    Red
     ↓
    Green
     ↓
    Refactor
     ↓
    Verification Pipeline
     ↓
    Commit

### Red Phase

Write a failing test that describes one desired behavior. The test must fail because the behavior is missing, not because of infrastructure issues.

### Green Phase

Implement the minimal code to make the test pass. Do exactly what the test requires, nothing more.

### Refactor Phase

Improve the code while keeping tests green. Extract common logic, improve naming, simplify structure.

### Verification Pipeline

Run the complete verification suite before committing.

### Commit

Create an atomic commit with a clear, conventional message.

## Verification Pipeline

The current Verification Pipeline consists of:

    ruff check .
    mypy src
    pytest -q

Success criteria:

- Ruff completes successfully
- Static type checking completes successfully
- All tests pass

All checks must succeed before committing. No exceptions.

## Engineering Playbook

The following rules are mandatory:

1. **One requirement per failing test.** Each Red test adds exactly one new behavior.

2. **Test behavior, not implementation.** Tests describe what the system does, not how it does it.

3. **Documentation describes existing state.** Documents describe implemented architecture, not planned architecture. Future plans belong in ROADMAP.

4. **Documentation formatting.** Documentation examples use four-space indentation for commands, code samples and directory trees. Generated project documentation does not use Markdown code fences.

5. **Visual review before moving on.** After creating or editing a document: output its contents, then run the full Verification Pipeline, then proceed to the next document.

6. **Static typing.** All code must satisfy the project's static type checking requirements.

7. **Atomic commits.** Each commit represents one logical change.

8. **Verification before commit.** The full Verification Pipeline must pass before every commit.

9. **Green state after commit.** Every commit must leave the repository in a releasable state. The Verification Pipeline must remain green.

## Commit Policy

Commits follow conventional format:

    type(scope): subject

    body

    footer

Types:

- feat: new feature
- fix: bug fix
- refactor: code refactoring
- docs: documentation
- test: tests
- chore: maintenance

Commit messages include verification summary in the footer:

    Verification:
    - Ruff: 0 errors
    - MyPy: 0 issues
    - Pytest: N passed

Documentation commits are separate from code commits when appropriate.
