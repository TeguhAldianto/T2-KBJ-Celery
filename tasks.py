from celery_app import app
import time
from datetime import datetime

@app.task(name="kbj_t2.test_task")
def test_task(message):
    print("=" * 50)
    print("WORKER MENERIMA PEKERJAAN")
    print(f"Pesan       : {message}")
    print(f"Waktu       : {datetime.now()}")
    print("=" * 50)

    time.sleep(3)

    return {
        "status": "success",
        "message": message,
        "processed_at": datetime.now().isoformat()
    }