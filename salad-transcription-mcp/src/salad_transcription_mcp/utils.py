"""Shared utilities."""

from __future__ import annotations

from typing import Any


def serialize_job(job: Any) -> dict:
    """Convert an SDK job object to a JSON-serializable dict.

    The Salad SDK attaches a ``_map()`` method via the ``@JsonMap`` decorator
    that handles field renames (e.g. ``id_`` → ``id``), enum serialization,
    and recursion into nested objects. Falls back to generic approaches for
    anything that doesn't carry ``_map``.
    """
    if hasattr(job, "_map"):
        return job._map()
    if hasattr(job, "to_dict"):
        return job.to_dict()
    if hasattr(job, "model_dump"):
        return job.model_dump()
    if hasattr(job, "dict"):
        return job.dict()
    raw = vars(job) if hasattr(job, "__dict__") else {}
    return {k: v for k, v in raw.items() if not k.startswith("__")}
