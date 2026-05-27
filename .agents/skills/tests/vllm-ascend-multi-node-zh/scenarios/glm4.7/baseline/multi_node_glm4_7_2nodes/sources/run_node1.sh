#!/bin/sh

# this obtained through ifconfig
# nic_name is the network interface name corresponding to local_ip of the current node
nic_name="xxxx"
local_ip="xxxx"
node0_ip="xxxx" # same as the local_IP address in node 0

export HCCL_IF_IP=$local_ip
export GLOO_SOCKET_IFNAME=$nic_name
export TP_SOCKET_IFNAME=$nic_name
export HCCL_SOCKET_IFNAME=$nic_name
export HCCL_BUFFSIZE=512
export OMP_PROC_BIND=false
export OMP_NUM_THREADS=1
export PYTORCH_NPU_ALLOC_CONF=expandable_segments:True
export HCCL_OP_EXPANSION_MODE=AIV
export VLLM_ASCEND_BALANCE_SCHEDULING=1
export VLLM_ASCEND_ENABLE_TOPK_OPTIMIZE=1

vllm serve Eco-Tech/GLM-4.7-W8A8-floatmtp \
  --host 0.0.0.0 \
  --port 8004 \
  --headless \
  --data-parallel-size 2 \
  --data-parallel-size-local 1 \
  --data-parallel-start-rank 1 \
  --data-parallel-address $node0_ip \
  --data-parallel-rpc-port 13389 \
  --tensor-parallel-size 8 \
  --enable-expert-parallel \
  --seed 1024 \
  --max-model-len 140000 \
  --max-num-batched-tokens 8192 \
  --max-num-seqs 16 \
  --async-scheduling \
  --quantization ascend \
  --trust-remote-code \
  --gpu-memory-utilization 0.9 \
  --enable-auto-tool-choice \
  --reasoning-parser glm45 \
  --tool-call-parser glm47 \
  --served-model-name glm47 \
  --speculative-config '{"num_speculative_tokens": 3, "method":"mtp"}' \
  --compilation-config '{"cudagraph_capture_sizes": [1,2,4,8,16,32,64,128,256,512], "cudagraph_mode": "FULL_DECODE_ONLY"}' \
  --additional-config '{"enable_shared_expert_dp": true, "ascend_fusion_config": {"fusion_ops_gmmswigluquant": false}}'