from celery import Celery  # type: ignore[import-untyped]
from kombu.entity import Exchange, Queue

app = Celery(
    "kbj_t2",
    broker="amqp://guest:guest@localhost:5672//",
    backend="rpc://",
    include=["tasks"],
)

# Exchange untuk demo skema message handling
fanout_exchange = Exchange("kbj.fanout", type="fanout")
topic_exchange = Exchange("kbj.topic", type="topic")

app.conf.update(  # type: ignore[reportUnknownMemberType]
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Jakarta",
    enable_utc=True,
    task_track_started=True,
    task_default_queue="default",
    task_default_exchange="default",
    task_default_routing_key="default",
    task_queues=(
        Queue("default"),
        # Fan-out: satu pesan broadcast ke semua queue yang terikat ke fanout exchange
        Queue("fanout.q1", exchange=fanout_exchange),
        Queue("fanout.q2", exchange=fanout_exchange),
        # Topic/Wildcard: routing_key dicocokkan dengan binding pattern
        Queue("topic.short", exchange=topic_exchange, routing_key="app.short"),
        Queue("topic.long", exchange=topic_exchange, routing_key="app.long"),
        Queue("topic.all", exchange=topic_exchange, routing_key="app.#"),  # wildcard # (0+ kata)
        Queue("topic.one", exchange=topic_exchange, routing_key="*.short"),  # wildcard * (1 kata)
    ),
    task_routes={
        "kbj_t2.short_task": {"queue": "default"},
        "kbj_t2.long_task": {"queue": "default"},
        "kbj_t2.fanout_task": {"queue": "fanout.q1"},  # default route; broadcast diatur saat publish
        "kbj_t2.topic_task": {"queue": "default"},
    },
)