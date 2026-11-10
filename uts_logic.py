import math
import time
from typing import Any, Dict

VALID_APPLICATIONS = {"SHORT", "LONG"}
MAX_LONG_ITERATIONS = 5_000_000
DEFAULT_LONG_ITERATIONS = 400_000


def execute_application(application_id: str, payload: Dict[str, Any], worker_id: str = "CELERY-WORKER") -> Any:
    """
    Logika aplikasi UTS (SHORT/LONG) yang sama persis, dijalankan sebagai tugas Celery.
    """
    if application_id == "SHORT":
        msg = payload.get("message", "")
        return msg

    if application_id == "LONG":
        iterations = int(payload.get("iterations", DEFAULT_LONG_ITERATIONS))
        msg = payload.get("message", "Komputasi Numerik")
        # Simulasi komputasi numerik deterministik & terbatas (aman dari infinite loop)
        accumulator = 0.0
        for i in range(1, iterations + 1):
            accumulator += math.sqrt(i) * math.sin(i % 90)
        # Tambahan jeda simulasi terukur (opsional dari payload, maks 2000 ms)
        sim_delay_ms = min(max(float(payload.get("simulated_delay_ms", 40.0)), 0.0), 2000.0)
        if sim_delay_ms > 0:
            time.sleep(sim_delay_ms / 1000.0)
        return {
            "summary": f"{msg} selesai pada {worker_id}",
            "iterations": iterations,
            "checksum": round(accumulator, 4),
        }

    raise ValueError(f"Application ID tidak didukung: {application_id}")
