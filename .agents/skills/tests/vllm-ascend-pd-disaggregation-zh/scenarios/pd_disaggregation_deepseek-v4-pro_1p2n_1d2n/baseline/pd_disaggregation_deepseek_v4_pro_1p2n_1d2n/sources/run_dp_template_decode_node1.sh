#!/bin/bash
# Decode node 1 template for DeepSeek-V4-Pro
# This script is parameterized by launch_online_dp.py

nic_name="eth0"
local_ip="192.168.1.30"

export LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libjemalloc.so.2:$LD_PRELOAD
export HCCL_OP_EXPANSION_MODE="AIV"
export TASK_QUEUE_ENABLE=1

export VLLM_RPC_TIMEOUT=3600000
export VLLM_EXECUTE_MODEL_TIMEOUT_SECONDS=30000
export HCCL_EXEC_TIMEOUT=2000
export HCCL_CONNECT_TIMEOUT=1200

export HCCL_IF_IP=$local_ip
export GLOO_SOCKET_IFNAME=$nic_name
export TP_SOCKET_IFNAME=$nic_name
export HCCL_SOCKET_IFNAME=$nic_name

export OMP_PROC_BIND=false
export OMP_NUM_THREADS=10
export PYTORCH_NPU_ALLOC_CONF=expandable_segments:True
export HCCL_BUFFSIZE=1024

export USE_MULTI_GROUPS_KV_CACHE=1
export USE_MULTI_BLOCK_POOL=1
export VLLM_ASCEND_ENABLE_FUSED_MC2=1
export ASCEND_RT_VISIBLE_DEVICES=$1

vllm serve /root/.cache/modelscope/hub/models/vllm-ascend/DeepSeek-V4-Pro-w4a8-mtp \
    --host 0.0.0.0 \
    --port $2 \
    --data-parallel-size $3 \
    --data-parallel-rank $4 \
    --data-parallel-address $5 \
    --data-parallel-rpc-port $6 \
    --tensor-parallel-size $7 \
    --enable-expert-parallel \
    --seed 1024 \
    --served-model-name auto \
    --max-model-len 131072 \
    --max-num-batched-tokens 120 \
    --max-num-seqs 60 \
    --async-scheduling \
    --block-size 128 \
    --tokenizer-mode deepseek_v4 \
    --tool-call-parser deepseek_v4 \
    --enable-auto-tool-choice \
    --reasoning-parser deepseek_v4 \
    --no-disable-hybrid-kv-cache-manager \
    --no-enable-prefix-caching \
    --safetensors-load-strategy 'prefetch' \
    --trust-remote-code \
    --gpu-memory-utilization 0.9 \
    --quantization ascend \
    --speculative-config '{"num_speculative_tokens": 1, "method":"deepseek_mtp"}' \
    --compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}' \
    --kv-transfer-config \
    '{"kv_connector": "MooncakeHybridConnector",
    "kv_role": "kv_consumer",
    "kv_port": "36200",
    "engine_id": "2",
    "kv_connector_extra_config": {
                "prefill": {
                        "dp_size": 4,
                        "tp_size": 8
                },
                "decode": {
                        "dp_size": 4,
                        "tp_size": 8
                }
        }
    }' \
    --additional-config '{
        "ascend_compilation_config":{
            "enable_npugraph_ex":true,
            "enable_static_kernel":false
        },
    "enable_cpu_binding":true,
    "multistream_overlap_shared_expert":false,
    "multistream_dsa_preprocess":false,
    "recompute_scheduler_enable":true
    }'