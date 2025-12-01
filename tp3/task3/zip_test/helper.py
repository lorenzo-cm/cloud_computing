WINDOW_SECONDS = 60
MEASUREMENT_PERIOD = 5
MAX_POINTS = WINDOW_SECONDS // MEASUREMENT_PERIOD


def update_cpu_history(
    input: dict, cpu_history: dict[str, list[float]]
) -> dict[str, list[float]]:
    cpu_keys = [k for k in input.keys() if k.startswith("cpu_percent-")]
    for key in cpu_keys:
        value = float(input[key])
        history = cpu_history.get(key, [])
        history.append(value)
        if len(history) > MAX_POINTS:
            history = history[-MAX_POINTS:]
        cpu_history[key] = history
    return cpu_history


def calculate_cpu_averages(cpu_history: dict[str, list[float]]) -> dict[str, float]:
    averages = {}
    for key, history in cpu_history.items():
        avg = sum(history) / len(history) if history else 0.0
        averages[f"avg-60sec-{key}"] = avg
    return averages


def calculate_network_egress_percent(input: dict) -> float:
    sent = float(input.get("net_io_counters_eth0-bytes_sent", 0.0))
    recv = float(input.get("net_io_counters_eth0-bytes_recv", 0.0))
    total_net = sent + recv
    if total_net > 0:
        return sent / total_net * 100.0
    return 0.0


def calculate_memory_cache_percent(input: dict) -> float:
    total_mem = float(input.get("virtual_memory-total", 1.0))
    buffers = float(input.get("virtual_memory-buffers", 0.0))
    cached = float(input.get("virtual_memory-cached", 0.0))
    return (buffers + cached) / total_mem * 100.0
