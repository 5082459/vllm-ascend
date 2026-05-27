#!/bin/bash
# Prefill Instance 5, Node 2 startup script
# Parameters: dp_size=12, tp_size=16, dp_size_local=1, dp_rank_start=1

python launch_online_dp.py     --dp-size 12     --tp-size 16     --dp-size-local 1     --dp-rank-start 1     --dp-address 192.168.1.109     --dp-rpc-port 12321     --vllm-start-port 7100
