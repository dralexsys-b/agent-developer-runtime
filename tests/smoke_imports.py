"""Smoke test: verify that all core packages can be imported.

This is a plain Python script (not pytest).
Run directly: python3 tests/smoke_imports.py

If any import fails, Python will raise ImportError and exit with non-zero code.
"""

import agent_runtime
import agent_runtime.kernel
import agent_runtime.domain
import agent_runtime.domain.events

print("✓ All core packages import successfully")
