#!/bin/bash
python launch_online_dp.py \
    --dp-size 1 \
    --tp-size 16 \
    --dp-size-local 1 \
    --dp-rank-start 0 \
    --dp-address 192.168.1.20 \
    --dp-rpc-port 12321 \
    --vllm-start-port 7100