#!/usr/bin/env python3
"""PD分离部署参数确定性计算工具.

用途：
- 把模型容易算错的参数（kv_port/engine_id/dp_rank_start/proxy hosts/ports）一次算完。
- 在 step-04（生成部署树）前调用一次，得到一份完整 plan，再去做文件生成。

使用：
    python compute_pd_params.py \
        --machine-type A3 \
        --prefill-instances 2 --nodes-per-prefill 1 \
        --decode-instances 1 --nodes-per-decode 1 \
        --prefill-tp-size 8 --decode-tp-size 4 \
        --prefill-ips 192.0.0.1 192.0.0.2 \
        --decode-ips 192.0.0.3 \
        --proxy-ip 192.0.0.100

参数计算规则与 references/appendix-pd-resources.md 中的公式严格一致。
所有规则均文档化在仓库内，本脚本只是把这些规则代码化以避免人工算术错误。
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from typing import List


# A3 超节点单机 16 卡，A2 单机 8 卡。
CARDS_PER_MACHINE = {"A3": 16, "A2": 8}

# kv_port 起步值：同时满足 A2 (>=28000) 和 A3 (>=36000) 的保留范围要求。
KV_PORT_BASE = 36000
KV_PORT_STEP = 100

# engine_id 从 1 起递增，Prefill 在前，Decode 接续。
ENGINE_ID_BASE = 1

# vllm serve 端口起点；每节点占用 dp_size_local 个连续端口。
VLLM_START_PORT = 7100


@dataclass
class NodePlan:
    role: str  # "prefill" | "decode"
    instance: int  # 1-based
    node: int  # 1-based
    ip: str
    instance_first_node_ip: str
    kv_port: int
    engine_id: int
    dp_rank_start: int
    dp_size: int
    dp_size_local: int
    tp_size: int
    vllm_ports: List[int]


@dataclass
class ProxyPlan:
    proxy_ip: str
    prefiller_hosts: List[str]
    prefiller_ports: List[int]
    decoder_hosts: List[str]
    decoder_ports: List[int]


@dataclass
class DeploymentPlan:
    machine_type: str
    cards_per_machine: int
    prefill_dp_size: int
    decode_dp_size: int
    prefill_dp_size_local: int
    decode_dp_size_local: int
    prefill_nodes: List[NodePlan] = field(default_factory=list)
    decode_nodes: List[NodePlan] = field(default_factory=list)
    proxy: ProxyPlan = field(default=None)


def _build_role_nodes(
    role: str,
    instances: int,
    nodes_per_instance: int,
    tp_size: int,
    cards_per_machine: int,
    ips: List[str],
    kv_port_start: int,
    engine_id_start: int,
) -> List[NodePlan]:
    """生成单一角色（prefill/decode）的所有节点参数."""
    if tp_size <= 0 or cards_per_machine % tp_size != 0:
        raise ValueError(
            f"{role} tp_size={tp_size} 不能整除单机卡数 {cards_per_machine}"
        )
    expected_ip_count = instances * nodes_per_instance
    if len(ips) != expected_ip_count:
        raise ValueError(
            f"{role} IP 数量不匹配：期望 {expected_ip_count}，实际 {len(ips)}"
        )

    dp_size_local = cards_per_machine // tp_size
    dp_size_total = instances * nodes_per_instance * dp_size_local

    nodes: List[NodePlan] = []
    ip_iter = iter(ips)
    for inst in range(1, instances + 1):
        first_ip = None
        for node_idx in range(1, nodes_per_instance + 1):
            ip = next(ip_iter)
            if node_idx == 1:
                first_ip = ip
            nodes.append(
                NodePlan(
                    role=role,
                    instance=inst,
                    node=node_idx,
                    ip=ip,
                    instance_first_node_ip=first_ip,
                    kv_port=kv_port_start + (inst - 1) * KV_PORT_STEP,
                    engine_id=engine_id_start + (inst - 1),
                    # dp_rank_start: 实例内按节点递增, 各实例独立计数。
                    dp_rank_start=(node_idx - 1) * dp_size_local,
                    dp_size=dp_size_total,
                    dp_size_local=dp_size_local,
                    tp_size=tp_size,
                    vllm_ports=[
                        VLLM_START_PORT + i for i in range(dp_size_local)
                    ],
                )
            )
    return nodes


def _build_proxy(
    proxy_ip: str,
    prefill_nodes: List[NodePlan],
    decode_nodes: List[NodePlan],
) -> ProxyPlan:
    """每个节点 IP 重复 dp_size_local 次，端口列表为 7100..7100+dp_size_local-1."""

    def expand(nodes: List[NodePlan]):
        hosts: List[str] = []
        ports: List[int] = []
        for n in nodes:
            hosts.extend([n.ip] * n.dp_size_local)
            ports.extend(n.vllm_ports)
        return hosts, ports

    p_hosts, p_ports = expand(prefill_nodes)
    d_hosts, d_ports = expand(decode_nodes)
    return ProxyPlan(
        proxy_ip=proxy_ip,
        prefiller_hosts=p_hosts,
        prefiller_ports=p_ports,
        decoder_hosts=d_hosts,
        decoder_ports=d_ports,
    )


def compute_plan(
    machine_type: str,
    prefill_instances: int,
    nodes_per_prefill: int,
    decode_instances: int,
    nodes_per_decode: int,
    prefill_tp_size: int,
    decode_tp_size: int,
    prefill_ips: List[str],
    decode_ips: List[str],
    proxy_ip: str,
) -> DeploymentPlan:
    if machine_type not in CARDS_PER_MACHINE:
        raise ValueError(
            f"machine_type 必须是 {list(CARDS_PER_MACHINE)} 之一，得到 {machine_type}"
        )
    cards = CARDS_PER_MACHINE[machine_type]

    prefill_nodes = _build_role_nodes(
        role="prefill",
        instances=prefill_instances,
        nodes_per_instance=nodes_per_prefill,
        tp_size=prefill_tp_size,
        cards_per_machine=cards,
        ips=prefill_ips,
        kv_port_start=KV_PORT_BASE,
        engine_id_start=ENGINE_ID_BASE,
    )

    # Decode 的 kv_port 接在 Prefill 之后；engine_id 全局接续。
    decode_kv_port_start = KV_PORT_BASE + prefill_instances * KV_PORT_STEP
    decode_engine_id_start = ENGINE_ID_BASE + prefill_instances
    decode_nodes = _build_role_nodes(
        role="decode",
        instances=decode_instances,
        nodes_per_instance=nodes_per_decode,
        tp_size=decode_tp_size,
        cards_per_machine=cards,
        ips=decode_ips,
        kv_port_start=decode_kv_port_start,
        engine_id_start=decode_engine_id_start,
    )

    proxy = _build_proxy(proxy_ip, prefill_nodes, decode_nodes)

    return DeploymentPlan(
        machine_type=machine_type,
        cards_per_machine=cards,
        prefill_dp_size=prefill_nodes[0].dp_size,
        decode_dp_size=decode_nodes[0].dp_size,
        prefill_dp_size_local=prefill_nodes[0].dp_size_local,
        decode_dp_size_local=decode_nodes[0].dp_size_local,
        prefill_nodes=prefill_nodes,
        decode_nodes=decode_nodes,
        proxy=proxy,
    )


def _parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--machine-type", required=True, choices=sorted(CARDS_PER_MACHINE))
    p.add_argument("--prefill-instances", type=int, required=True)
    p.add_argument("--nodes-per-prefill", type=int, required=True)
    p.add_argument("--decode-instances", type=int, required=True)
    p.add_argument("--nodes-per-decode", type=int, required=True)
    p.add_argument("--prefill-tp-size", type=int, required=True)
    p.add_argument("--decode-tp-size", type=int, required=True)
    p.add_argument("--prefill-ips", nargs="+", required=True,
                   help="按 P1N1 P1N2 P2N1 ... 顺序")
    p.add_argument("--decode-ips", nargs="+", required=True,
                   help="按 D1N1 D1N2 D2N1 ... 顺序")
    p.add_argument("--proxy-ip", required=True)
    p.add_argument("--output", default="-",
                   help="输出 JSON 路径；- 表示 stdout（默认）")
    return p.parse_args(argv)


def main(argv: List[str]) -> int:
    args = _parse_args(argv)
    plan = compute_plan(
        machine_type=args.machine_type,
        prefill_instances=args.prefill_instances,
        nodes_per_prefill=args.nodes_per_prefill,
        decode_instances=args.decode_instances,
        nodes_per_decode=args.nodes_per_decode,
        prefill_tp_size=args.prefill_tp_size,
        decode_tp_size=args.decode_tp_size,
        prefill_ips=args.prefill_ips,
        decode_ips=args.decode_ips,
        proxy_ip=args.proxy_ip,
    )
    payload = json.dumps(asdict(plan), indent=2, ensure_ascii=False)
    if args.output == "-":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
