#!/bin/bash

# Proxy startup script for DeepSeek-V4-Pro PD disaggregation (2P2N 1D2N)
# Using layerwise proxy (MooncakeHybridConnector)

PROXY_HOST="192.168.1.40"
PROXY_PORT="1999"

# Prefill nodes configuration (dp_size_local=2, each IP repeated twice)
# Instance1: P1N1=192.168.1.20, P1N2=192.168.1.21
# Instance2: P2N1=192.168.1.22, P2N2=192.168.1.23
PREFILLER_HOSTS="192.168.1.20 192.168.1.20 192.168.1.21 192.168.1.21 192.168.1.22 192.168.1.22 192.168.1.23 192.168.1.23"
PREFILLER_PORTS="7100 7101 7100 7101 7100 7101 7100 7101"

# Decode nodes configuration (dp_size_local=2, each IP repeated twice)
# Instance1: D1N1=192.168.1.30, D1N2=192.168.1.31
DECODER_HOSTS="192.168.1.30 192.168.1.30 192.168.1.31 192.168.1.31"
DECODER_PORTS="7100 7101 7100 7101"

python load_balance_proxy_layerwise_server_example.py \
    --host $PROXY_HOST \
    --port $PROXY_PORT \
    --prefiller-hosts $PREFILLER_HOSTS \
    --prefiller-ports $PREFILLER_PORTS \
    --decoder-hosts $DECODER_HOSTS \
    --decoder-ports $DECODER_PORTS