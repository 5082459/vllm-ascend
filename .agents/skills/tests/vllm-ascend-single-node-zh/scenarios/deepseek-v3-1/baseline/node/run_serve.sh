#!/bin/sh
# this obtained through ifconfig
# nic_name is the network interface name corresponding to local_ip of the current node
nic_name="eth0"
local_ip="192.168.1.100"

# [Optional] jemalloc
# jemalloc is for better performance, if `libjemalloc.so` is installed on your machine, you can turn it on.
# export LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libjemalloc.so.2:$LD_PRELOAD

# AIV
export HCCL_OP_EXPANSION_MODE="AIV"

export HCCL_IF_IP=$local_ip
export GLOO_SOCKET_IFNAME=$nic_name
export TP_SOCKET_IFNAME=$nic_name
export HCCL_SOCKET_IFNAME=$nic_name
export VLLM_ASCEND_BALANCE_SCHEDULING=1
export PYTORCH_NPU_ALLOC_CONF=expandable_segments:True

vllm serve /root/.cache/DeepSeek-V3.1 \
--host 0.0.0.0 \
--port 8015 \
--data-parallel-size 4 \
--tensor-parallel-size 4 \
--quantization ascend \
--seed 1024 \
--served-model-name deepseek_v3 \
--enable-expert-parallel \
--async-scheduling \
--max-num-seqs 16 \
--max-model-len 16384 \
--max-num-batched-tokens 4096 \
--trust-remote-code \
--no-enable-prefix-caching \
--gpu-memory-utilization 0.92 \
--speculative-config '{"num_speculative_tokens": 3, "method": "mtp"}' \
--compilation-config '{"cudagraph_capture_sizes":[4,16,32,48,64], "cudagraph_mode": "FULL_DECODE_ONLY"}'