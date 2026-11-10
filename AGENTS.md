# AGENTS.md

## Ringkasan
- App Celery `kbj_t2` (`celery_app.py`): broker `amqp://guest:guest@localhost:5672//`, backend `rpc://` (hardcoded). Task terdaftar via `include=["tasks"]`.
- Porting logika UTS socket-load-balancer: SHORT (echo `payload.message`) & LONG (komputasi numerik deterministik; `iterations` default 400k, max 5M; `simulated_delay_ms` 0–2000ms, default 40) di `uts_logic.py:execute_application`.
- Tidak ada automated tests, lint, typecheck, atau CI. Hindari commit artefak env/cache (`.venv/`, `__pycache__/`).

## File kunci / entrypoint
- `celery_app.py`: konfigurasi app; exchange/queue `kbj.fanout`→`fanout.q1,q2`; `kbj.topic` binding `app.short`→`topic.short`, `app.long`→`topic.long`, `app.#`→`topic.all`, `*.short`→`topic.one`; `task_routes` short/long→`default`.
- `tasks.py`: `kbj_t2.short_task(request_id,payload)`, `kbj_t2.long_task(request_id,payload)`, `kbj_t2.fanout_task`, `kbj_t2.topic_task`, `kbj_t2.test_task` (sleep 3s).
- `producer.py`: CLI/input generator (`--mode default|fanout|topic`, `--app SHORT|LONG`, `--routing-key`, `--count`, `--force-error`, `--no-wait`). `default` menunggu hasil (timeout 60s) kecuali `--no-wait`; fanout/topic hanya cetak task id.
- `requirements.txt`: `celery`, `flower`, `kombu`.

## Langkah menjalankan project (Windows, detail)
### 1) Prasyarat
- Python 3.10+ dan RabbitMQ aktif di `localhost:5672` (akun default `guest:guest`).
- Buka terminal/PowerShell di root repo: `C:\laragon\www\Python\T2-KBJ-Celery`.

### 2) Siapkan environment & dependency
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
Jika aktivasi diblokir: jalankan `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` lalu aktifkan lagi.

### 3) Jalankan worker Celery (wajib `-P solo` di Windows)
Pilih sesuai skenario, jalankan di terminal terpisah (aktifkan `.venv` di tiap terminal):

- **Default / UTS SHORT-LONG** (queue `default`):
```powershell
celery -A celery_app worker --loglevel=info -P solo -Q default
```

- **Demo Fan-out** (dua worker, masing-masing konsumsi satu queue agar broadcast terlihat):
```powershell
# Terminal A
celery -A celery_app worker --loglevel=info -P solo -Q fanout.q1 -n fan1@%h
# Terminal B
celery -A celery_app worker --loglevel=info -P solo -Q fanout.q2 -n fan2@%h
```

- **Demo Topic/Wildcard** (satu worker konsumsi semua queue topic):
```powershell
celery -A celery_app worker --loglevel=info -P solo -Q topic.short,topic.long,topic.all,topic.one -n topic@%h
```

### 4) Jalankan producer (di terminal lain, `.venv` aktif)
- **UTS SHORT (echo, menunggu hasil):**
```powershell
python producer.py --mode default --app SHORT --req-id REQ-001 --message "Halo UTS"
```
- **UTS LONG (komputasi, menunggu hasil):**
```powershell
python producer.py --mode default --app LONG --req-id REQ-002 --message "Komputasi" --iterations 400000 --delay-ms 40
```
  Tambah `--no-wait` jika tidak ingin menunggu hasil.
- **Fan-out (broadcast ke `fanout.q1` & `fanout.q2`):**
```powershell
python producer.py --mode fanout --message "Broadcast ke semua"
```
- **Topic/Wildcard:**
```powershell
python producer.py --mode topic --routing-key app.short --message "pesan short"
python producer.py --mode topic --routing-key app.long  --message "pesan long"
python producer.py --mode topic --routing-key other.short --message "uji wildcard *"
```

### 5) (Opsional) Monitoring Flower
```powershell
celery -A celery_app flower
```
Buka UI di alamat yang ditampilkan (default `http://localhost:5555`).

### 6) Hentikan
`Ctrl+C` di terminal worker/flower/producer.

## Catatan perilaku & routing
- Fan-out (`kbj.fanout`): routing key diabaikan, 1 publish → semua queue terikat (`fanout.q1`, `fanout.q2`).
- Topic (`kbj.topic`): `app.short` → `topic.short`,`topic.all`(`app.#`),`topic.one`(`*.short`); `app.long` → `topic.long`,`topic.all`; `other.short` → `topic.one` saja (tidak match `app.#`).
- Pastikan RabbitMQ hidup sebelum start worker/producer; tanpa worker pada queue terkait, fanout/topic tidak terlihat diproses (producer hanya kirim).