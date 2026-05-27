#!/bin/bash
# Proxy startup script for GLM5.1 PD Disaggregation (6P2N 4D2N)
# Basic version - uses load_balance_proxy_server_example.py

PROXY_TYPE="basic"  # "basic" or "layerwise"
PROXY_PORT="1999"
PROXY_HOST="192.168.3.1"

# Prefill nodes configuration
# dp_size_local=1 for Prefill (tp_size=16)
# Each node runs 1 vLLM process on port 7100
# 6 instances × 2 nodes = 12 nodes total
PREFILLER_HOSTS="192.168.1.101 192.168.1.102 192.168.1.103 192.168.1.104 192.168.1.105 192.168.1.106 192.168.1.107 192.168.1.108 192.168.1.109 192.168.1.110 192.168.1.111 192.168.1.112"
PREFILLER_PORTS="7100 7100 7100 7100 7100 7100 7100 7100 7100 7100 7100 7100"

# Decode nodes configuration
# dp_size_local=4 for Decode (tp_size=4)
# Each node runs 4 vLLM processes on ports 7100-7103
# 4 instances × 2 nodes = 8 nodes total, each ×4 = 32 entries
DECODER_HOSTS="192.168.2.101 192.168.2.101 192.168.2.101 192.168.2.101 \
192.168.2.102 192.168.2.102 192.168.2.102 192.168.2.102 \
192.168.2.103 192.168.2.103 192.168.2.103 192.168.2.103 \
192.168.2.104 192.168.2.104 192.168.2.104 192.168.2.104 \
192.168.2.105 192.168.2.105 192.168.2.105 192.168.2.105 \
192.168.2.106 192.168.2.106 192.168.2.106 192.168.2.106 \
192.168.2.107 192.168.2.107 192.168.2.107 192.168.2.107 \
192.168.2.108 192.168.2.108 192.168.2.108 192.168.2.108"

DECODER_PORTS="7100 7101 7102 7103 \
7100 7101 7102 7103 \
7100 7101 7102 7103 \
7100 7101 7102 7103 \
7100 7101 7102 7103 \
7100 7101 7102 7103 \
7100 7101 7102 7103 \
7100 7101 7102 7103"

if [ "$PROXY_TYPE" == "basic" ]; then
    python load_balance_proxy_server_example.py \
        --port $PROXY_PORT \
        --host $PROXY_HOST \
        --prefiller-hosts $PREFILLER_HOSTS \
        --prefiller-ports $PREFILLER_PORTS \
        --decoder-hosts $DECODER_HOSTS \
        --decoder-ports $DECODER_PORTS
else
    python load_balance_proxy_layerwise_server_example.py \
        --port $PROXY_PORT \
        --host $PROXY_HOST \
        --prefiller-hosts $PREFILLER_HOSTS \
        --prefiller-ports $PREFILLER_PORTS \
        --decoder-hosts $DECODER_HOSTS \
        --decoder-ports $DECODER_PORTS
fi