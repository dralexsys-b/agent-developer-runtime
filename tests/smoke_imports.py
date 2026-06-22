"""Smoke test: verify that all core packages can be imported.

This is a plain Python script (not pytest).
Run directly: python3 tests/smoke_imports.py

If any import fails, Python will raise ImportError and exit with non-zero code.
"""

import agent_runtime
import agent_runtime.domain
import agent_runtime.domain.events
import agent_runtime.kernel

from agent_runtime.kernel import SystemClock, Timestamp

clock = SystemClock()
now = clock.now()
assert now.tzinfo is not None, "SystemClock must return aware datetime"

ts = Timestamp.now()
assert ts.to_datetime().tzinfo is not None, "Timestamp must be UTC-aware"

print("✓ All core packages import successfully")
print("✓ Kernel public API is accessible")
print("✓ Basic timestamp creation works (timezone-aware)")
