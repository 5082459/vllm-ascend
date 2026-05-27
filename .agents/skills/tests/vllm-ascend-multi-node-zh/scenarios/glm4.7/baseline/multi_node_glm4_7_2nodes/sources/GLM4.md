# GLM-4.5/4.6/4.7

## Introduction

GLM-4.x series models use a Mixture-of-Experts (MoE) architecture and are foundational models specifically designed for agent applications.

The `GLM-4.5` model is first supported in `vllm-ascend:v0.10.0rc1`.

This document will show the main verification steps of the model, including supported features, feature configuration, environment preparation, single-node and multi-node deployment, accuracy and performance evaluation.

## Supported Features

Refer to [supported features](../../user_guide/support_matrix/supported_models.md) to get the model's supported feature matrix.

Refer to [feature guide](../../user_guide/feature_guide/index.md) to get the feature's configuration.

## Environment Preparation

### Model Weight

- `GLM-4.5`(BF16 version): [Download model weight](https://www.modelscope.cn/models/ZhipuAI/GLM-4.5).
- `GLM-4.6`(BF16 version): [Download model weight](https://www.modelscope.cn/models/ZhipuAI/GLM-4.6).
- `GLM-4.7`(BF16 version): [Download model weight](https://www.modelscope.cn/models/ZhipuAI/GLM-4.7).
- `GLM-4.5-w8a8-with-float-mtp`(Quantized version with mtp): [Download model weight](https://modelers.cn/models/Modelers_Park/GLM-4.5-w8a8).
- `GLM-4.6-w8a8`(Quantized version without mtp): [Download model weight](https://modelers.cn/models/Modelers_Park/GLM-4.6-w8a8). Because vllm does not support GLM4.6 mtp in October, we do not provide an mtp version. Last month, it was supported; you can use the following quantization scheme to add mtp weights to the quantized weights.
- `GLM-4.7-w8a8-with-float-mtp`(Quantized version without mtp): [Download model weight](https://modelscope.cn/models/Eco-Tech/GLM-4.7-W8A8-floatmtp).
- `Method of Quantization`: [quantization scheme](https://ai.gitcode.com/Ascend-SACT/GLM-4.5-w8a8). You can use these methods to quantify the model.

It is recommended to download the model weight to the shared directory of multiple nodes, such as `/root/.cache/`.

### Installation

You can use our official docker image to run `GLM-4.x` directly.

:::::{tab-set}
:sync-group: install

::::{tab-item} A3 series
:sync: A3

Start the docker image on each node.

```{code-block} bash
   :substitutions:

export IMAGE=quay.io/ascend/vllm-ascend:|vllm_ascend_version|-a3
docker run --rm \
    --name vllm-ascend \
    --shm-size=1g \
    --net=host \
    --device /dev/davinci0 \
    --device /dev/davinci1 \
    --device /dev/davinci2 \
    --device /dev/davinci3 \
    --device /dev/davinci4 \
    --device /dev/davinci5 \
    --device /dev/davinci6 \
    --device /dev/davinci7 \
    --device /dev/davinci8 \
    --device /dev/davinci9 \
    --device /dev/davinci10 \
    --device /dev/davinci11 \
    --device /dev/davinci12 \
    --device /dev/davinci13 \
    --device /dev/davinci14 \
    --device /dev/davinci15 \
    --device /dev/davinci_manager \
    --device /dev/devmm_svm \
    --device /dev/hisi_hdc \
    -v /usr/local/dcmi:/usr/local/dcmi \
    -v /usr/local/Ascend/driver/tools/hccn_tool:/usr/local/Ascend/driver/tools/hccn_tool \
    -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
    -v /usr/local/Ascend/driver/lib64/:/usr/local/Ascend/driver/lib64/ \
    -v /usr/local/Ascend/driver/version.info:/usr/local/Ascend/driver/version.info \
    -v /etc/ascend_install.info:/etc/ascend_install.info \
    -v /root/.cache:/root/.cache \
    -it $IMAGE bash
```

::::
::::{tab-item} A2 series
:sync: A2

Start the docker image on your each node.

```{code-block} bash
   :substitutions:

export IMAGE=quay.io/ascend/vllm-ascend:|vllm_ascend_version|
docker run --rm \
    --name vllm-ascend \
    --shm-size=1g \
    --net=host \
    --device /dev/davinci0 \
    --device /dev/davinci1 \
    --device /dev/davinci2 \
    --device /dev/davinci3 \
    --device /dev/davinci4 \
    --device /dev/davinci5 \
    --device /dev/davinci6 \
    --device /dev/davinci7 \
    --device /dev/davinci_manager \
    --device /dev/devmm_svm \
    --device /dev/hisi_hdc \
    -v /usr/local/dcmi:/usr/local/dcmi \
    -v /usr/local/Ascend/driver/tools/hccn_tool:/usr/local/Ascend/driver/tools/hccn_tool \
    -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
    -v /usr/local/Ascend/driver/lib64/:/usr/local/Ascend/driver/lib64/ \
    -v /usr/local/Ascend/driver/version.info:/usr/local/Ascend/driver/version.info \
    -v /etc/ascend_install.info:/etc/ascend_install.info \
    -v /root/.cache:/root/.cache \
    -it $IMAGE bash
```

::::
:::::

In addition, if you don't want to use the docker image as above, you can also build all from source:

- Install `vllm-ascend` from source, refer to [installation](../../installation.md).

If you want to deploy multi-node environment, you need to set up environment on each node.

## Deployment

### Single-node Deployment

- In low-latency scenarios, we recommend a single-machine deployment.
- Quantized model `glm4.7_w8a8_with_float_mtp` can be deployed on 1 Atlas 800 A3 (64G × 16) or 1 Atlas 800 A2 (64G × 8).

Run the following script to execute online inference.

```shell
#!/bin/sh
export HCCL_BUFFSIZE=512
export OMP_PROC_BIND=false
export OMP_NUM_THREADS=1
export PYTORCH_NPU_ALLOC_CONF=expandable_segments:True
export HCCL_OP_EXPANSION_MODE=AIV
export VLLM_ASCEND_BALANCE_SCHEDULING=1
export VLLM_ASCEND_ENABLE_TOPK_OPTIMIZE=1

vllm serve Eco-Tech/GLM-4.7-W8A8-floatmtp \
  --data-parallel-size 2 \
  --tensor-parallel-size 8 \
  --enable-expert-parallel \
  --seed 1024 \
  --served-model-name glm \
  --max-model-len 133000 \
  --max-num-batched-tokens 8192 \
  --max-num-seqs 16 \
  --async-scheduling \
  --quantization ascend \
  --trust-remote-code \
  --gpu-memory-utilization 0.9 \
  --speculative-config '{"num_speculative_tokens": 3, "method":"mtp"}' \
  --compilation-config '{"cudagraph_capture_sizes": [1,2,4,8,16,32,64,128,256,512], "cudagraph_mode": "FULL_DECODE_ONLY"}' \
  --additional-config '{"enable_shared_expert_dp": true, "ascend_fusion_config": {"fusion_ops_gmmswigluquant": false}}'
```

**Notice:**
The parameters are explained as follows:

- `--async-scheduling` Asynchronous scheduling is a technique used to optimize inference efficiency. It allows non-blocking task scheduling to improve concurrency and throughput, especially when processing large-scale models.
- `fusion_ops_gmmswigluquant` The performance of the GmmSwigluQuant fusion operator tends to degrade when the total number of NPUs is ≤ 16.
- `VLLM_ASCEND_ENABLE_FLASHCOMM1` Due to the FD feature of the FIA operator being invalidated by padding data introduced by this feature, we recommend disabling the `flashcomm1` feature for long-sequence (≥16k) and low-concurrency (≤8 batch size) scenarios.For long-sequence and high-concurrency scenarios, you may enable this feature to achieve improved Prefill performance.

### Multi-node Deployment

Although the former tutorial said "Not recommended to deploy multi-node on Atlas 800 A2 (64G × 8)", but if you insist to deploy GLM-4.x model on multi-node like 2 × Atlas 800 A2 (64G × 8), run the following scripts on two nodes respectively.

**Node 0**

```shell
#!/bin/sh

# this obtained through ifconfig
# nic_name is the network interface name corresponding to local_ip of the current node
nic_name="xxxx"
local_ip="xxxx"

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
  --data-parallel-size 2 \
  --data-parallel-size-local 1 \
  --data-parallel-start-rank 0 \
  --data-parallel-address $local_ip \
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
```

**Node 1**

```shell
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
```

## Functional Verification

Once your server is started, you can query the model with input prompts:

```shell
curl -H "Accept: application/json" \
    -H "Content-type: application/json" \
    -X POST \
    -d '{
        "model": "glm", 
        "messages": [{ 
            "role": "user", 
            "content": "The future of AI is" 
        }], 
        "stream": false, 
        "ignore_eos": false, 
        "temperature": 0, 
        "max_tokens": 200 
    }' http://<node0_ip>:<port>/v1/chat/completions
```

## Accuracy Evaluation

Here are two accuracy evaluation methods.

### Using AISBench

1. Refer to [Using AISBench](../../developer_guide/evaluation/using_ais_bench.md) for details.

2. After execution, you can get the result, here is the result of `GLM4.7` in `vllm-ascend:main` (after `vllm-ascend:0.14.0rc1`) for reference only.

| dataset | version | metric | mode | vllm-api-general-chat | note |
|----- | ----- | ----- | ----- | -----| ----- |
| GPQA | - | accuracy | gen | 84.85 | 1 Atlas 800 A3 (64G × 16) |
| MATH500 | - | accuracy | gen | 98.8 | 1 Atlas 800 A3 (64G × 16) |

### Using Language Model Evaluation Harness

Not tested yet.

## Performance

### Using AISBench

Refer to [Using AISBench for performance evaluation](../../developer_guide/evaluation/using_ais_bench.md#execute-performance-evaluation) for details.

### Using vLLM Benchmark

Run performance evaluation of `GLM-4.x` as an example.

Refer to [vllm benchmark](https://docs.vllm.ai/en/latest/benchmarking/) for more details.

There are three `vllm bench` subcommands:

- `latency`: Benchmark the latency of a single batch of requests.
- `serve`: Benchmark the online serving throughput.
- `throughput`: Benchmark offline inference throughput.

Take the `serve` as an example. Run the code as follows.

```shell
vllm bench serve \
  --backend vllm \
  --dataset-name prefix_repetition \
  --prefix-repetition-prefix-len 22400 \
  --prefix-repetition-suffix-len 9600 \
  --prefix-repetition-output-len 1024 \
  --num-prompts 1 \
  --prefix-repetition-num-prefixes 1 \
  --ignore-eos \
  --model glm \
  --tokenizer Eco-Tech/GLM-4.7-W8A8-floatmtp \
  --seed 1000 \
  --host 0.0.0.0 \
  --port 8000 \
  --endpoint /v1/completions \
  --max-concurrency 1 \
  --request-rate 1
```

After about several minutes, you can get the performance evaluation result.

## Best Practices

In this chapter, we recommend best practices for three scenarios:

- Long-context: For long sequences with low concurrency (≤ 4): set `dp1 tp16`; For long sequences with high concurrency (> 4): set `dp2 tp8`
- Low-latency: For short sequences with low latency: we recommend setting `dp2 tp8`
- High-throughput: For short sequences with high throughput: we also recommend setting `dp2 tp8`

**Notice:**
`max-model-len` and `max-num-seqs` need to be set according to the actual usage scenario. For other settings, please refer to the **[Deployment](#deployment)** chapter.

## FAQ

- **Q: Startup fails with HCCL port conflicts (address already bound). What should I do?**

  A: Clean up old processes and restart: `pkill -f VLLM*`.

- **Q: How to handle OOM or unstable startup?**

  A: Reduce `--max-num-seqs` and `--max-model-len` first. If needed, reduce concurrency and load-testing pressure (e.g., `max-concurrency` / `num-prompts`).