# Architecture

## Overview

Agent Developer Runtime follows Domain-Driven Design (DDD) and Clean Architecture principles. The system is organized into layers with clear boundaries and dependency rules.

## Layer Structure

    ┌─────────────────────────────────────┐
    │           Domain Layer              │
    │  ┌───────────────────────────────┐  │
    │  │   AggregateRoot (base)        │  │
    │  │   - Event queue               │  │
    │  │   - _record_event()           │  │
    │  │   - pull_events()             │  │
    │  └───────────────────────────────┘  │
    │  ┌───────────────────────────────┐  │
    │  │   Value Objects               │  │
    │  │   - AgentId, TaskId           │  │
    │  │   - TaskStatus                │  │
    │  └───────────────────────────────┘  │
    │  ┌───────────────────────────────┐  │
    │  │   Domain Events               │  │
    │  │   - AgentRenamed              │  │
    │  │   - TaskTitleChanged          │  │
    │  │   - TaskStarted               │  │
    │  │   - TaskCompleted             │  │
    │  └───────────────────────────────┘  │
    │  ┌───────────────────────────────┐  │
    │  │   Aggregates                  │  │
    │  │   - Agent                     │  │
    │  │   - Task                      │  │
    │  └───────────────────────────────┘  │
    ├─────────────────────────────────────┤
    │           Kernel Layer              │
    │  - Clock, Result, IDs, Timestamp    │
    │  - Base types and interfaces        │
    └─────────────────────────────────────┘

## Dependency Rules

- Inner layers know nothing about outer layers
- Domain depends only on Kernel
- Kernel has no dependency on Domain
- All dependencies point inward

## Core Concepts

### AggregateRoot

Base class for all aggregates providing domain event infrastructure.

    class AggregateRoot:
        _events: list[DomainEvent]
        
        def _record_event(self, event: DomainEvent) -> None
        def pull_events(self) -> list[DomainEvent]

### Value Objects

Immutable types with structural equality:

- AgentId: UUID-based agent identifier
- TaskId: UUID-based task identifier
- TaskStatus: Enum (PENDING, IN_PROGRESS, COMPLETED)
- Timestamp: Point in time

### Domain Events

Facts about things that happened in the domain:

- AgentRenamed(agent_id, old_name, new_name)
- TaskTitleChanged(task_id, old_title, new_title)
- TaskStarted(task_id)
- TaskCompleted(task_id)

All events inherit from DomainEvent base class with event_type and occurred_at.

### Aggregates

**Agent**

Represents an autonomous agent.

Operations:

- rename(new_name) emits AgentRenamed

Invariants:

- Non-empty name

**Task**

Represents a unit of work with lifecycle management.

Operations:

- change_title(new_title) emits TaskTitleChanged
- start() emits TaskStarted (PENDING to IN_PROGRESS)
- complete() emits TaskCompleted (IN_PROGRESS to COMPLETED)

Invariants:

- Non-empty title
- Cannot complete non-started task
- Status transitions: PENDING to IN_PROGRESS to COMPLETED

## Domain Event Flow

All state changes emit domain events:

    task.start()

    events = task.pull_events()
    # [TaskStarted(task_id=...)]

## Design Principles

1. **Ubiquitous Language**: Code reflects domain concepts
2. **Encapsulation**: Aggregates protect their invariants
3. **Immutability**: Value objects are frozen dataclasses
4. **Domain Events**: State changes publish domain events
5. **Strict Typing**: MyPy strict mode enforced
6. **Test-Driven**: Every behavior tested before implementation

## Testing Strategy

- Aggregate behavior
- Domain invariants
- Domain events
- Verification Pipeline
