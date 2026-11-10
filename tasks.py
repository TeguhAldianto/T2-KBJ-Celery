import socket
import time
from datetime import datetime
from typing import Any

from celery_app import app
from uts_logic import DEFAULT_LONG_ITERATIONS, execute_application


def _task_meta(extra: dict[str, Any] | None = None) -> dict[str, Any]:
    meta: dict[str, Any] = {
        "worker_hostname": socket.gethostname(),
        "processed_at": datetime.now().isoformat(),
    }
    if extra:
        meta.update(extra)
    return meta


@app.task(name="kbj_t2.short_task")  # type: ignore[reportUntypedFunctionDecorator, reportUnknownMemberType]
def short_task(request_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    start = time.perf_counter()
    result: Any
    try:
        result = execute_application("SHORT", payload)
        status = "success"
    except Exception as exc:
        result = str(exc)
        status = "error"
    elapsed_ms = round((time.perf_counter() - start) * 1000, 3)
    return {
        "message_type": "response",
        "request_id": request_id,
        "application_id": "SHORT",
        "status": status,
        "result": result,
        "processing_time_ms": elapsed_ms,
        **_task_meta(),
    }


@app.task(name="kbj_t2.long_task")  # type: ignore[reportUntypedFunctionDecorator, reportUnknownMemberType]
def long_task(request_id: str, payload: dict[str, Any] | None) -> dict[str, Any]:
    payload_data: dict[str, Any] = dict(payload or {})
    payload_data.setdefault("iterations", DEFAULT_LONG_ITERATIONS)
    start = time.perf_counter()
    result: Any
    try:
        result = execute_application("LONG", payload_data)
        status = "success"
    except Exception as exc:
        result = str(exc)
        status = "error"
    elapsed_ms = round((time.perf_counter() - start) * 1000, 3)
    return {
        "message_type": "response",
        "request_id": request_id,
        "application_id": "LONG",
        "status": status,
        "result": result,
        "processing_time_ms": elapsed_ms,
        **_task_meta({"iterations": payload_data.get("iterations")}),
    }


@app.task(name="kbj_t2.fanout_task")  # type: ignore[reportUntypedFunctionDecorator, reportUnknownMemberType]
def fanout_task(message: str, source: str = "fanout") -> dict[str, Any]:
    # Diterima oleh semua queue yang terikat ke fanout exchange (broadcast)
    return {
        "task": "fanout_task",
        "message": message,
        "source": source,
        **_task_meta(),
    }


@app.task(name="kbj_t2.topic_task")  # type: ignore[reportUntypedFunctionDecorator, reportUnknownMemberType]
def topic_task(message: str, routing_key: str = "") -> dict[str, Any]:
    # Dikirim ke queue berdasarkan kecocokan routing_key dengan binding pattern
    return {
        "task": "topic_task",
        "message": message,
        "routing_key": routing_key,
        **_task_meta(),
    }


# Backward-compatible contoh task awal
@app.task(name="kbj_t2.test_task")  # type: ignore[reportUntypedFunctionDecorator, reportUnknownMemberType]
def test_task(message: str) -> dict[str, Any]:
    time.sleep(3)
    return {
        "status": "success",
        "message": message,
        "processed_at": datetime.now().isoformat(),
    }