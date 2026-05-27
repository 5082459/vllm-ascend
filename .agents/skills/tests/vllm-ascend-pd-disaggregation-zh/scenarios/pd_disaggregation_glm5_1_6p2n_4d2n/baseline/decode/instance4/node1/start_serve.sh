#!/bin/bash
# Decode Instance 4, Node 1 startup script
# Parameters: dp_size=32, tp_size=4, dp_size_local=4, dp_rank_start=24

python launch_online_dp.py     --dp-size 32     --tp-size 4     --dp-size-local 4     --dp-rank-start 24     --dp-address 192.168.2.107     --dp-rpc-port 12321     --vllm-start-port 7100
