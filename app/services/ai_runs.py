"""Record every AI call as one task and one execution, including failures."""

from __future__ import annotations

import json
import time
import uuid

from app.ai import provider
from app.ai.tasks import TASKS
from app.db import utc_now
from app.permissions import permission_scope


def execute(
    db,
    *,
    task_type: str,
    user,
    task_input: dict,
    context: dict,
) -> dict:
    """Run the adapter and persist the task/execution pair.

    A failing adapter never raises to the caller: the execution is stored with
    status ``fallback`` and a labelled output. An unknown task type is a caller
    bug and raises before anything is recorded.
    """
    if task_type not in TASKS:
        raise ValueError(f"unknown task type: {task_type}")
    started = time.perf_counter()
    try:
        result = provider.run(task_type, context)
        status = "succeeded"
    except Exception as error:  # the seam must degrade, not break the request
        result = {
            "output": {
                "fallback": True,
                "message": "The assistant could not interpret this request; "
                "permitted facts are unchanged.",
                "reason": type(error).__name__,
            },
            "model": "demo-orchestrator/fallback",
            "reasoning": "fallback",
            "cost_usd": 0.0,
            "tools_used": 0,
            "validation": "fallback",
        }
        status = "fallback"

    latency_ms = max(1, int((time.perf_counter() - started) * 1000))
    task_id = f"AI-{uuid.uuid4().hex[:6].upper()}"
    scope = permission_scope(user)
    db.execute(
        "INSERT INTO ai_tasks (id, task_type, user_id, permission_scope, input, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (
            task_id,
            task_type,
            user["id"] if user is not None else None,
            json.dumps(scope),
            json.dumps(task_input, default=str),
            utc_now(),
        ),
    )
    cursor = db.execute(
        "INSERT INTO ai_executions (task_id, model, reasoning, tools_used, latency_ms, cost_usd, "
        "status, validation, output, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            task_id,
            result["model"],
            result["reasoning"],
            result["tools_used"],
            latency_ms,
            result["cost_usd"],
            status,
            result["validation"],
            json.dumps(result["output"], default=str),
            utc_now(),
        ),
    )
    db.commit()
    return {
        "task_id": task_id,
        "execution_id": cursor.lastrowid,
        "status": status,
        "model": result["model"],
        "latency_ms": latency_ms,
        "cost_usd": result["cost_usd"],
        "validation": result["validation"],
        "output": result["output"],
    }
