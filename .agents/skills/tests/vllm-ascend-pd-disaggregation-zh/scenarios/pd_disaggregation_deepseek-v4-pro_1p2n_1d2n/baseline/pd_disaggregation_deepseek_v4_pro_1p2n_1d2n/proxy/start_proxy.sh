#!/bin/bash
# Proxy startup script for DeepSeek-V4-Pro PD Disaggregation (1P2N 1D2N)
# Basic version - uses load_balance_proxy_server_example.py

PROXY_TYPE="basic"  # "basic" or "layerwise"
PROXY_PORT="1999"
PROXY_HOST="192.168.1.40"

# Prefill nodes configuration
# Each node IP repeated dp_size_local times (dp_size_local=2)
# PREFILLER_HOSTS format: P1N1_IP P1N1_IP P1N2_IP P1N2_IP
PREFILLER_HOSTS="192.168.1.20 192.168.1.20 192.168.1.21 192.168.1.21"
# PREFILLER_PORTS format: 7100 7101 for each node (vllm_start_port + dp_size_local - 1)
PREFILLER_PORTS="7100 7101 7100 7101"

# Decode nodes configuration
# Each node IP repeated dp_size_local times (dp_size_local=2)
# DECODER_HOSTS format: D1N1_IP D1N1_IP D1N2_IP D1N2_IP
DECODER_HOSTS="192.168.1.30 192.168.1.30 192.168.1.31 192.168.1.31"
# DECODER_PORTS format: 7100 7101 for each node
DECODER_PORTS="7100 7101 7100 7101"

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