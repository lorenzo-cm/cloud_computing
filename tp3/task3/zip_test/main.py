import logging
from typing import Any

from helper import (
    calculate_cpu_averages,
    calculate_memory_cache_percent,
    calculate_network_egress_percent,
    update_cpu_history,
)


def handler(input: dict, context: object) -> dict[str, Any]:
    logging.info("Rodando com context: ", context)

    if not hasattr(context, "env") or context.env is None:
        context.env = {}

    env = context.env
    cpu_history: dict[str, list[float]] = env.get("cpu_history", {})

    cpu_history = update_cpu_history(input, cpu_history)
    env["cpu_history"] = cpu_history

    output: dict[str, Any] = {}
    output["cpu_history"] = cpu_history

    cpu_averages = calculate_cpu_averages(cpu_history)
    output.update(cpu_averages)

    output["percent-network-egress"] = calculate_network_egress_percent(input)
    output["percent-memory-cache"] = calculate_memory_cache_percent(input)

    return output
