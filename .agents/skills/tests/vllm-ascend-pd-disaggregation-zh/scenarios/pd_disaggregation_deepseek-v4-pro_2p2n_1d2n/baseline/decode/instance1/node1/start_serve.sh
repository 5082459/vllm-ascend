#!/bin/bash
python launch_online_dp.py \
    --dp-size 4 \
    --tp-size 8 \
    --dp-size-local 2 \
    --dp-rank-start 0 \
    --dp-address 192.168.1.30 \
    --dp-rpc-port 12321 \
    --vllm-start-port 7100