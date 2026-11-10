import argparse
import json

from celery_app import fanout_exchange, topic_exchange
from tasks import fanout_task, long_task, short_task, topic_task
from uts_logic import DEFAULT_LONG_ITERATIONS


def send_default(app_id: str, request_id: str, message: str, iterations: int, delay_ms: float, wait: bool):
    if app_id == "SHORT":
        async_result = short_task.delay(request_id, {"message": message})  # type: ignore[attr-defined]
    elif app_id == "LONG":
        async_result = long_task.delay(  # type: ignore[attr-defined]
            request_id,
            {"message": message, "iterations": iterations, "simulated_delay_ms": delay_ms},
        )
    else:
        raise ValueError("app harus SHORT atau LONG")
    print(f"[PRODUCER:default] task_id={async_result.id} app={app_id} request_id={request_id}")
    if wait:
        print(json.dumps(async_result.get(timeout=60), indent=2, ensure_ascii=False))


def send_fanout(message: str):
    # Fan-out: exchange meng-broadcast pesan ke semua queue yang terikat (fanout.q1, fanout.q2)
    async_result = fanout_task.apply_async(  # type: ignore[attr-defined]
        args=[message, "fanout-exchange"],
        exchange=fanout_exchange,
        routing_key="",  # diabaikan pada fanout
    )
    print(f"[PRODUCER:fanout] task_id={async_result.id} exchange=kbj.fanout -> fanout.q1, fanout.q2")
    print("Catatan: satu publish diproses oleh setiap queue terikat (butuh worker konsumsi queue tsb).")


def send_topic(routing_key: str, message: str):
    # Topic: routing_key dicocokkan dengan binding pattern (app.short, app.long, app.#, *.short)
    async_result = topic_task.apply_async(  # type: ignore[attr-defined]
        args=[message, routing_key],
        exchange=topic_exchange,
        routing_key=routing_key,
    )
    print(f"[PRODUCER:topic] task_id={async_result.id} exchange=kbj.topic routing_key={routing_key}")


def main():
    parser = argparse.ArgumentParser(description="Producer Celery (porting UTS + demo fanout/topic/wildcard)")
    parser.add_argument("--mode", choices=["default", "fanout", "topic"], default="default")
    parser.add_argument("--app", choices=["SHORT", "LONG"], default="SHORT")
    parser.add_argument("--req-id", default="REQ-001")
    parser.add_argument("--message", default="Halo dari client")
    parser.add_argument("--iterations", type=int, default=DEFAULT_LONG_ITERATIONS)
    parser.add_argument("--delay-ms", type=float, default=40.0)
    parser.add_argument("--routing-key", default="app.short", help="untuk mode topic, mis: app.short, app.long, other.short")
    parser.add_argument("--no-wait", action="store_true", help="jangan tunggu hasil (berguna untuk fanout/topic)")
    args = parser.parse_args()

    if args.mode == "default":
        send_default(args.app, args.req_id, args.message, args.iterations, args.delay_ms, wait=not args.no_wait)
    elif args.mode == "fanout":
        send_fanout(args.message)
    elif args.mode == "topic":
        send_topic(args.routing_key, args.message)


if __name__ == "__main__":
    main()