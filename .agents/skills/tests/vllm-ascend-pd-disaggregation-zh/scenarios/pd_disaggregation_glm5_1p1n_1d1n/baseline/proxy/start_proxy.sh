#!/bin/bash
# Proxy startup script for GLM5 PD disaggregation (1P1N 1D1N)

PROXY_TYPE="basic"  # "basic" or "layerwise"
PROXY_PORT="1999"
PROXY_HOST="192.168.1.40"

# Prefill nodes configuration
# dp_size_local for prefill = 1 (16 cards / tp_size 16)
PREFILLER_HOSTS="192.168.1.20"
PREFILLER_PORTS="7100"

# Decode nodes configuration
# dp_size_local for decode = 4 (16 cards / tp_size 4)
# Each decode node runs 4 DP ranks, ports 7100-7103
DECODER_HOSTS="192.168.1.30 192.168.1.30 192.168.1.30 192.168.1.30"
DECODER_PORTS="7100 7101 7102 7103"

unset http_proxy
unset https_proxy

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