# T2-KBJ-Celery

Implementasi Tugas 2 KBJ (Job Queue dengan Celery & RabbitMQ), sekaligus **porting logika UTS** (`socket-load-balancer`) ke Celery agar selinier:
- Aplikasi UTS **SHORT** (echo pesan) dan **LONG** (komputasi numerik deterministik + delay terukur) diimplementasikan sebagai task Celery di `tasks.py` (logika inti di `uts_logic.py`, sama persis dengan UTS).
- `producer.py` berperan sebagai pengganti client/producer UTS: mengirim pekerjaan ke broker RabbitMQ untuk diproses worker Celery.
- Alokasi beban (round-robin/least-served) pada UTS kini ditangani oleh mekanisme distribusi Celery/RabbitMQ ke worker/queue.

## Prasyarat
- Python 3.10+
- RabbitMQ berjalan di `localhost:5672` (default `guest:guest`)
- Virtual environment `.venv`

## Instalasi
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## Struktur
- `celery_app.py`: Konfigurasi app `kbj_t2` (broker AMQP, backend RPC) + deklarasi exchange & queue untuk fanout/topic.
- `uts_logic.py`: Logika aplikasi UTS (`execute_application`) SHORT/LONG (sama persis).
- `tasks.py`: Task Celery `short_task`, `long_task`, `fanout_task`, `topic_task` (+ `test_task` kompatibilitas).
- `producer.py`: Producer/input generator (mode default/fanout/topic).

## Menjalankan (Windows)

### 1. Worker (default queue, untuk SHORT/LONG)
```bash
celery -A celery_app worker --loglevel=info -P solo -Q default
```

### 2. Producer - porting UTS (SHORT/LONG)
```bash
# SHORT (echo)
python producer.py --mode default --app SHORT --req-id REQ-001 --message "Halo UTS"

# LONG (komputasi numerik)
python producer.py --mode default --app LONG --req-id REQ-002 --message "Komputasi" --iterations 400000 --delay-ms 40
```

### 3. Flower (opsional)
```bash
celery -A celery_app flower
```

## Demo Message Handling (Fan-Out, Topic, Wildcard)

> Catatan: Jalankan worker yang mendengarkan queue terkait agar pesan terlihat diproses.

### Fan-Out
- **Konsep**: Exchange tipe `fanout` menyalin (broadcast) satu pesan ke **semua queue** yang terikat ke exchange tersebut; `routing_key` diabaikan.
- **Konfigurasi**: exchange `kbj.fanout` terikat ke `fanout.q1` dan `fanout.q2` (`celery_app.py`).
- **Worker** (dua worker/terminal, masing-masing konsumsi satu queue):
```bash
celery -A celery_app worker --loglevel=info -P solo -Q fanout.q1 -n fan1@%h
celery -A celery_app worker --loglevel=info -P solo -Q fanout.q2 -n fan2@%h
```
- **Producer**:
```bash
python producer.py --mode fanout --message "Broadcast ke semua"
```
- **Hasil**: pesan yang sama diterima/diproses oleh `fanout.q1` dan `fanout.q2`.

### Topic + Wildcard
- **Konsep**: Exchange tipe `topic` merutekan pesan ke queue berdasarkan kecocokan `routing_key` dengan **binding pattern**.
  - `*` (wildcard): cocok tepat **satu kata**.
  - `#` (wildcard): cocok **nol atau lebih kata**.
- **Konfigurasi** (exchange `kbj.topic`):
  - `topic.short` ← binding `app.short`
  - `topic.long`  ← binding `app.long`
  - `topic.all`   ← binding `app.#` (wildcard `#`, terima semua yang diawali `app.`)
  - `topic.one`   ← binding `*.short` (wildcard `*`, terima `<satu-kata>.short`)
- **Worker** (contoh konsumsi beberapa queue):
```bash
celery -A celery_app worker --loglevel=info -P solo -Q topic.short,topic.long,topic.all,topic.one -n topic@%h
```
- **Producer**:
```bash
python producer.py --mode topic --routing-key app.short --message "pesan short"
python producer.py --mode topic --routing-key app.long  --message "pesan long"
python producer.py --mode topic --routing-key other.short --message "uji wildcard *"
```
- **Perkiraan hasil routing**:
  - `app.short`   → `topic.short`, `topic.all` (`app.#`), `topic.one` (`*.short`)
  - `app.long`    → `topic.long`, `topic.all`
  - `other.short` → `topic.one` (`*.short`), **bukan** `topic.all` (tidak match `app.#`)

## Perbedaan Singkat Fan-Out vs Topic vs Wildcard
| Skema | Exchange | Dasar routing | Kapan dipakai |
|---|---|---|---|
| **Fan-Out** | `fanout` | Broadcast ke semua queue terikat; `routing_key` diabaikan | Notifikasi/broadcast ke banyak consumer |
| **Topic** | `topic` | `routing_key` dicocokkan dengan binding pattern pada queue | Routing selektif berdasarkan kategori/topik |
| **Wildcard** (pada Topic) | `topic` | `*` = 1 kata, `#` = 0+ kata dalam pattern | Fleksibilitas filter (subset/semua turunan topik) |

## Catatan
- Di Windows worker Celery harus memakai pool `-P solo`.
- Pastikan RabbitMQ aktif sebelum menjalankan worker/producer.
- Konfigurasi broker/backend hardcoded di `celery_app.py` (`amqp://guest:guest@localhost:5672//`, backend `rpc://`).
