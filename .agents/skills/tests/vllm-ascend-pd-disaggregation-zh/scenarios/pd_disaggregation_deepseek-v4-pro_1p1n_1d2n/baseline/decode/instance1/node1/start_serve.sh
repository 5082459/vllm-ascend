#!/bin/bash
# Decode Instance 1, Node 1 startup script
# Parameters: dp_size=4, tp_size=8, dp_size_local=2, dp_rank_start=0

python launch_online_dp.py \
    --dp-size 4 \
    --tp-size 8 \
    --dp-size-local 2 \
    --dp-rank-start 0 \
    --dp-address 192.168.1.30 \
    --dp-rpc-port 12321 \
    --vllm-start-port 7100