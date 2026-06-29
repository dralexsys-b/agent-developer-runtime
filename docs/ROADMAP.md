# Roadmap

Development roadmap for Agent Developer Runtime.

## Current Status

Core Domain v1 — completed.

- Kernel Layer (Clock, Result, IDs, Timestamp)
- Domain Layer (Aggregates, Value Objects, Domain Events)
- AggregateRoot with domain event infrastructure
- Task lifecycle (PENDING → IN_PROGRESS → COMPLETED)
- Verification Pipeline (pytest, mypy, ruff)

## Near-term Direction

Transition beyond Core Domain.

- Persistence layer
- Application Layer

This roadmap reflects the current direction and will evolve as the project architecture evolves.

## Related Documentation

Architectural decisions (ADR), evidence logs, and project knowledge base are maintained in agent-developer-memory.
