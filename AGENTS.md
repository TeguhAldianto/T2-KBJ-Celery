# AGENTS.md

## Overview & Architecture
Python Celery task queue repo.
- `celery_app.py`: Celery app (`kbj_t2`) configured for RabbitMQ broker and RPC backend.
- `tasks.py`: Celery task definitions (`kbj_t2.test_task`).
- `producer.py`: Test script dispatching tasks and waiting up to 30s for RPC output.

## Prerequisites
- **RabbitMQ**: Broker running on `amqp://guest:guest@localhost:5672//`.

## Execution Commands
Use virtual environment (`.venv`):

- **Start Celery Worker (Windows)**:
  `celery -A celery_app worker --loglevel=info -P solo`
  *(Use `-P solo` pool on Windows to avoid process pool errors)*

- **Run Producer**:
  `python producer.py`

- **Start Flower Monitoring Dashboard**:
  `celery -A celery_app flower`
