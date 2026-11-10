from celery import Celery

app = Celery(
    "kbj_t2",
    broker="amqp://guest:guest@localhost:5672//",
    backend="rpc://",
    include=["tasks"]
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Jakarta",
    enable_utc=True,
    task_track_started=True,
)