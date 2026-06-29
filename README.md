# Agent Developer Runtime

Runtime framework for code generation and validation (Beta-0.1a).

## Project Status

**Current milestone: Core Domain v1**

- Verification Pipeline passing
- Strict MyPy typing enabled
- Test-Driven Development process established
- Domain-Driven Design principles applied

## What Is This?

A Domain-Driven Design implementation providing core runtime primitives for code generation and validation. This repository provides the foundational runtime and domain model for the Agent Developer project.

## What's Implemented

- Kernel layer
- Domain layer
- Task lifecycle
- Domain event infrastructure
- Verification pipeline

## Development

    source .venv/bin/activate
    pytest -q
    mypy src
    ruff check .

All changes follow strict TDD: Red → Green → Refactor → Verification Pipeline → Commit.

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for methodology details.

## Documentation

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — System architecture
- [docs/ROADMAP.md](docs/ROADMAP.md) — Development roadmap
- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) — Development process
- [CHANGELOG.md](CHANGELOG.md) — Version history

## Related Repositories

- [agent-developer-memory](https://github.com/dralexsys-b/agent-developer-memory): Architectural decisions (ADR), evidence logs, and project knowledge base
