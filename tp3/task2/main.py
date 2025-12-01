import os
import json
from typing import Any

import redis
import streamlit as st


def get_redis_client() -> redis.Redis:
    redis_host = os.getenv("REDIS_HOST", "192.168.121.171")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))
    redis_db = int(os.getenv("REDIS_DB", "0"))

    return redis.Redis(
        host=redis_host,
        port=redis_port,
        db=redis_db,
        decode_responses=True,
    )


def load_metrics(r: redis.Redis, output_key: str) -> dict[str, Any] | None:
    raw = r.get(output_key)
    if raw is None:
        return None

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None

    return data


def parse_cpu_metrics(data: dict[str, Any]) -> list[tuple[str, float]]:
    cpu_items: list[tuple[str, float]] = []

    for key, value in data.items():
        if key.startswith("avg-60sec-cpu_percent-"):
            cpu_id = key.split("-")[-1]
            label = f"CPU {cpu_id}"
            cpu_items.append((label, float(value)))

    cpu_items.sort(key=lambda x: x[0])
    return cpu_items


def get_metrics():
    r = get_redis_client()
    output_key = os.getenv(
        "REDIS_OUTPUT_KEY",
        "f6939046d4b2aa170232bf5ef9631f01-ifs4-proj3-output",
    )

    data = load_metrics(r, output_key)
    if data is None:
        return None

    cpu_items = parse_cpu_metrics(data)

    percent_memory_cache = float(data.get("percent-memory-cache", 0.0))
    percent_network_egress = float(data.get("percent-network-egress", 0.0))

    return {
        "cpu_items": cpu_items,
        "percent_memory_cache": percent_memory_cache,
        "percent_network_egress": percent_network_egress,
    }


def main():
    st.set_page_config(
        page_title="Monitoring Dashboard",
        layout="wide",
    )

    st.title("Monitoring Dashboard")

    st.write("Clique no botão abaixo para atualizar as métricas.")
    if st.button("Atualizar"):
        st.rerun()

    metrics = get_metrics()

    if metrics is None:
        st.warning("Nenhum dado encontrado ainda no Redis.")
        st.stop()

    cpu_items = metrics["cpu_items"]
    percent_network_egress = metrics["percent_network_egress"]
    percent_memory_cache = metrics["percent_memory_cache"]

    st.subheader("% Network Egress and % Memory Cache")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            label="Percentual de tráfego de saída (bytes sent / total)",
            value=f"{percent_network_egress:.2f} %",
        )

    with col2:
        st.metric(
            label="Percentual de memória em cache (buffers + cached / total)",
            value=f"{percent_memory_cache:.2f} %",
        )

    st.markdown("---")

    st.subheader("Utilização média das CPUs (últimos 60s)")

    if cpu_items:
        cpu_labels = [label for label, _ in cpu_items]
        cpu_values = [val for _, val in cpu_items]

        st.table(
            {
                "CPU": cpu_labels,
                "Utilização média (últimos 60s) [%]": [f"{v:.2f}" for v in cpu_values],
            }
        )

        st.bar_chart(
            {
                "CPU Utilization (%)": cpu_values,
            }
        )
    else:
        st.info("Ainda não há dados de utilização de CPU para exibir.")


if __name__ == "__main__":
    main()
