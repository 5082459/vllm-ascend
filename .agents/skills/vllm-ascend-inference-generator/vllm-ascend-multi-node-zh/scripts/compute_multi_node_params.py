#!/usr/bin/env python3
"""Deterministic parameter calculator for vllm-ascend multi-node deployment.

Computes per-node dp_size_local, dp_size_total, and dp_rank_start so that
references/step-04-generate.md doesn't have to rederive them by hand.

Usage:
    python compute_multi_node_params.py \
        --machine-type A3 \
        --node-count 2 \
        --tp-size 8 \
        --node-ips 192.168.1.1 192.168.1.2 \
        --output deploy.plan.json
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from typing import List

CARDS_PER_MACHINE = {"A3": 16, "A2": 8}
DEFAULT_RPC_PORT = 13389


@dataclass
class NodePlan:
    node_index: int
    ip: str
    dp_rank_start: int
    headless: bool


@dataclass
class DeploymentPlan:
    machine_type: str
    cards_per_machine: int
    tp_size: int
    dp_size_local: int
    dp_size_total: int
    node_count: int
    node0_ip: str
    rpc_port: int
    nodes: List[NodePlan]


def compute_plan(
    machine_type: str,
    node_count: int,
    tp_size: int,
    node_ips: List[str],
) -> DeploymentPlan:
    if machine_type not in CARDS_PER_MACHINE:
        raise ValueError(
            f"machine_type must be one of {list(CARDS_PER_MACHINE)}, got {machine_type!r}"
        )
    if len(node_ips) != node_count:
        raise ValueError(
            f"node-ips length ({len(node_ips)}) must equal node-count ({node_count})"
        )
    cards = CARDS_PER_MACHINE[machine_type]
    if cards % tp_size != 0:
        raise ValueError(
            f"cards_per_machine ({cards}) must be divisible by tp_size ({tp_size})"
        )
    dp_size_local = cards // tp_size
    dp_size_total = dp_size_local * node_count

    nodes: List[NodePlan] = []
    for i, ip in enumerate(node_ips):
        nodes.append(
            NodePlan(
                node_index=i,
                ip=ip,
                dp_rank_start=i * dp_size_local,
                headless=(i != 0),
            )
        )

    return DeploymentPlan(
        machine_type=machine_type,
        cards_per_machine=cards,
        tp_size=tp_size,
        dp_size_local=dp_size_local,
        dp_size_total=dp_size_total,
        node_count=node_count,
        node0_ip=node_ips[0],
        rpc_port=DEFAULT_RPC_PORT,
        nodes=nodes,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--machine-type", required=True, choices=list(CARDS_PER_MACHINE))
    parser.add_argument("--node-count", type=int, required=True)
    parser.add_argument("--tp-size", type=int, required=True)
    parser.add_argument("--node-ips", nargs="+", required=True, help="Per-node IPs in order")
    parser.add_argument("--output", help="If set, write plan to this JSON file")
    args = parser.parse_args()

    plan = compute_plan(
        machine_type=args.machine_type,
        node_count=args.node_count,
        tp_size=args.tp_size,
        node_ips=args.node_ips,
    )
    payload = {
        "machine_type": plan.machine_type,
        "cards_per_machine": plan.cards_per_machine,
        "tp_size": plan.tp_size,
        "dp_size_local": plan.dp_size_local,
        "dp_size_total": plan.dp_size_total,
        "node_count": plan.node_count,
        "node0_ip": plan.node0_ip,
        "rpc_port": plan.rpc_port,
        "nodes": [asdict(n) for n in plan.nodes],
    }

    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text)
            f.write("\n")
    print(text)


if __name__ == "__main__":
    main()
