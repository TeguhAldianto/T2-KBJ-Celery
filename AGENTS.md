# AGENTS.md

## What this is
Celery app `kbj_t2` (RabbitMQ broker `amqp://guest:guest@localhost:5672//`, backend `rpc://`) porting UTS `socket-load-balancer` SHORT/LONG logic to tasks. Broker/backend/queues are hardcoded in `celery_app.py`.

## Key files
- `celery_app.py`: app config; exchanges/queues `kbj.fanout`→`fanout.q1,q2`, `kbj.topic` bindings `app.short`, `app.long`, `app.#` (`topic.all`), `*.short` (`topic.one`); routes `short_task/long_task`→`default`.
- `uts_logic.py`: `execute_application(app, payload)` — SHORT echoes `payload.message`; LONG does deterministic numeric work (`iterations`, default 400k, max 5M) + optional `simulated_delay_ms` (clamped 0–2000, default 40) and returns checksum/summary.
- `tasks.py`: Celery tasks `kbj_t2.short_task`, `kbj_t2.long_task`, `kbj_t2.fanout_task`, `kbj_t2.topic_task` (+ `kbj_t2.test_task`, sleeps 3s).
- `producer.py`: CLI (`--mode default|fanout|topic`, `--app SHORT|LONG`, `--routing-key`, `--no-wait`). `default` waits for result by default; fanout/topic print task id only.

## Run (Windows)
- Prereqs: RabbitMQ on `localhost:5672`, use `.venv` (`pip install -r requirements.txt`: celery, flower, kombu). **Workers must use `-P solo` on Windows.**
- Default/UTS worker: `celery -A celery_app worker --loglevel=info -P solo -Q default`
- UTS produce: `python producer.py --mode default --app SHORT|LONG [--req-id ... --message ... --iterations ... --delay-ms ...] [--no-wait]`
- Fanout demo: workers `-Q fanout.q1 -n fan1@%h` and `-Q fanout.q2 -n fan2@%h` (separate terminals), then `python producer.py --mode fanout --message "..."`
- Topic demo: worker `-Q topic.short,topic.long,topic.all,topic.one -n topic@%h`, then `python producer.py --mode topic --routing-key app.short|app.long|other.short --message "..."`
- Flower: `celery -A celery_app flower`

## Notes
- No automated tests, lint, typecheck, or CI configured. `__pycache__/` and `.venv/` exist in repo; avoid committing generated/env artifacts.
