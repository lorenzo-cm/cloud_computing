from typing import Any
import logging

WINDOW_SECONDS = 60
MEASUREMENT_PERIOD = 5
MAX_POINTS = WINDOW_SECONDS // MEASUREMENT_PERIOD  # 12

def handler(input: dict, context: object) -> dict[str, Any]:
    logging.info("Rodando com context: ", context)

    if not hasattr(context, "env") or context.env is None:
        context.env = {}

    env = context.env
    cpu_history: dict[str, list[float]] = env.get("cpu_history", {})

    cpu_keys = [k for k in input.keys() if k.startswith("cpu_percent-")]
    for key in cpu_keys:
        value = float(input[key])
        history = cpu_history.get(key, [])
        history.append(value)
        if len(history) > MAX_POINTS:
            history = history[-MAX_POINTS:]
        cpu_history[key] = history

    env["cpu_history"] = cpu_history

    output: dict[str, Any] = {}

    output["cpu_history"] = cpu_history

    for key, history in cpu_history.items():
        avg = sum(history) / len(history) if history else 0.0
        output[f"avg-60sec-{key}"] = avg

    sent = float(input.get("net_io_counters_eth0-bytes_sent", 0.0))
    recv = float(input.get("net_io_counters_eth0-bytes_recv", 0.0))
    total_net = sent + recv
    if total_net > 0:
        output["percent-network-egress"] = sent / total_net * 100.0
    else:
        output["percent-network-egress"] = 0.0

    total_mem = float(input.get("virtual_memory-total", 1.0))
    buffers = float(input.get("virtual_memory-buffers", 0.0))
    cached = float(input.get("virtual_memory-cached", 0.0))
    output["percent-memory-cache"] = (buffers + cached) / total_mem * 100.0

    return output