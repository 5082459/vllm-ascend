#!/bin/sh
# DeepSeek-V3.1 Multi-node Deployment - Node 1 (Worker)
# Machine Type: A3 (16 cards)
# Deployment: DP=4, DP_local=2, TP=8

# this obtained through ifconfig
# nic_name is the network interface name corresponding to local_ip of the current node
nic_name="eth0"
local_ip="<NODE1_IP>"

# The value of node0_ip must be consistent with the value of local_ip set in node0 (master node)
node0_ip="192.168.1.10"

# [Optional] jemalloc
# jemalloc is for better performance, if `libjemalloc.so` is installed on your machine, you can turn it on.
# export LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libjemalloc.so.2:$LD_PRELOAD

export HCCL_IF_IP=$local_ip
export GLOO_SOCKET_IFNAME=$nic_name
export TP_SOCKET_IFNAME=$nic_name
export HCCL_SOCKET_IFNAME=$nic_name
export OMP_PROC_BIND=false
export OMP_NUM_THREADS=1
export HCCL_BUFFSIZE=200
export PYTORCH_NPU_ALLOC_CONF=expandable_segments:True
export VLLM_ASCEND_BALANCE_SCHEDULING=1
export HCCL_INTRA_PCIE_ENABLE=1
export HCCL_INTRA_ROCE_ENABLE=0

vllm serve /root/.cache/DeepSeek-V3.1 \
--host 0.0.0.0 \
--port 8004 \
--headless \
--data-parallel-size 4 \
--data-parallel-size-local 2 \
--data-parallel-start-rank 2 \
--data-parallel-address $node0_ip \
--data-parallel-rpc-port 13389 \
--tensor-parallel-size 8 \
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