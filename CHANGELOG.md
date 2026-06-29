# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0-dev0] - 2026-06-28

### Core Domain v1 Milestone

Core Domain v1 milestone establishing the Kernel and Domain layers.

#### Added

**Kernel Layer**

- Clock interface and implementation
- Result type for error handling
- Typed identity value objects (AgentId, TaskId)
- Timestamp value object
- Base type definitions

**Domain Events**

- DomainEvent base class with event_type and occurred_at
- Domain event infrastructure
- AgentRenamed event
- TaskTitleChanged event
- TaskStarted event
- TaskCompleted event

**Value Objects**

- AgentId (UUID-based)
- TaskId (UUID-based)
- TaskStatus (PENDING, IN_PROGRESS, COMPLETED)

**Aggregates**

- AggregateRoot base class with event sourcing
- Agent aggregate with rename() operation
- Task aggregate with full lifecycle

**Task Lifecycle**

- change_title() emits TaskTitleChanged
- start() emits TaskStarted (PENDING to IN_PROGRESS)
- complete() emits TaskCompleted (IN_PROGRESS to COMPLETED)
- Domain invariants: non-empty title, IN_PROGRESS before completion

**Quality Infrastructure**

- Full Verification Pipeline (pytest, mypy, ruff)
- Strict type checking (MyPy strict mode)
- Contract tests covering implemented domain behavior

### Principles

- Test-Driven Development: Red, Green, Refactor
- Domain-Driven Design: Aggregates, Value Objects, Domain Events
- Clean Architecture: separation of concerns, dependency inversion
- Event Sourcing: all state changes emit domain events
- Strict Typing: MyPy strict mode enforced
