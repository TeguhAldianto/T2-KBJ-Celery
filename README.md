# T2-KBJ-Celery

Project pengujian task queue berbasis Celery dan RabbitMQ.

## Prasyarat
- Python 3.10+
- RabbitMQ running di `localhost:5672` (default: `guest:guest`)

## Instalasi
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## Cara Jalankan

1. **Jalankan Celery Worker (Windows)**
   ```bash
   celery -A celery_app worker --loglevel=info -P solo
   ```

2. **Jalankan Producer (Kirim Task)**
   ```bash
   python producer.py
   ```

3. **Jalankan Dashboard Flower (Optional)**
   ```bash
   celery -A celery_app flower
   ```
