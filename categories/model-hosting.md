---
category: model-hosting
tools:
  - { name: "vLLM",      repo: "vllm-project/vllm" }
  - { name: "Ollama",    repo: "ollama/ollama" }
  - { name: "llama.cpp", repo: "ggml-org/llama.cpp" }
  - { name: "SGLang",    repo: "sgl-project/sglang" }
last_reviewed: 2026-04-26
---

# Model Hosting

## Overview
Running open-weights models yourself. Picks depend on hardware and workload shape, not popularity.

## Decision heuristics
- Laptop dev, occasional use → Ollama (or LM Studio for GUI).
- CPU-only or embedded → llama.cpp directly.
- GPU server, throughput-oriented → vLLM.
- Heavy structured generation, prefix-cached agentic workloads → SGLang.
- HF ecosystem alignment, inference endpoints → Text Generation Inference (TGI).

## What to verify per workload
- Concurrency: how many simultaneous requests? vLLM and SGLang are built for this; Ollama is not.
- KV cache reuse: agent loops with shared prefixes benefit massively from RadixAttention (SGLang) or prefix caching (vLLM).
- Quantization support: GGUF (llama.cpp/Ollama) vs. AWQ/GPTQ/FP8 (vLLM/SGLang) — the model release dictates options as much as the server does.
- OpenAI compatibility: all the serious servers expose it; LiteLLM in front normalizes any remaining gaps.

## Tools

<!-- BEGIN TOOL: vllm-project/vllm -->
### vLLM
<!-- repo: vllm-project/vllm -->

#### What it is
High-throughput LLM inference server. PagedAttention for KV-cache memory efficiency; speculative decoding, prefix caching, multi-LoRA, OpenAI-compatible API.

#### When to reach for it
- Self-hosting open models on GPUs at any meaningful concurrency.
- Need OpenAI-compatible endpoints with high throughput.

#### When not to
- Laptop/dev — use Ollama or llama.cpp.
- CPU-only — use llama.cpp.

#### How it fits with other tools
Sits behind LiteLLM / OpenRouter as a backend. SGLang and TGI are direct competitors.

#### Sources
- Repo: https://github.com/vllm-project/vllm
<!-- END TOOL: vllm-project/vllm -->

<!-- BEGIN TOOL: ollama/ollama -->
### Ollama
<!-- repo: ollama/ollama -->

#### What it is
Run open models locally with one command. llama.cpp under the hood, friendly CLI, REST API, and a model registry.

#### When to reach for it
- Laptop/dev experimentation with open models.
- Lightweight self-host for small teams.

#### When not to
- Production multi-tenant serving — use vLLM/SGLang/TGI.

#### Sources
- Repo: https://github.com/ollama/ollama
<!-- END TOOL: ollama/ollama -->

<!-- BEGIN TOOL: ggml-org/llama.cpp -->
### llama.cpp
<!-- repo: ggml-org/llama.cpp -->

#### What it is
CPU-first (and GPU-capable) C++ inference engine. The substrate under Ollama, LM Studio, and many embedded uses. GGUF model format originated here.

#### When to reach for it
- CPU-only or constrained-edge inference.
- You need fine control or to embed inference into a larger app.

#### When not to
- High-throughput multi-tenant GPU serving — vLLM/SGLang win on raw throughput and operational ergonomics.

#### Sources
- Repo: https://github.com/ggml-org/llama.cpp
<!-- END TOOL: ggml-org/llama.cpp -->

<!-- BEGIN TOOL: sgl-project/sglang -->
### SGLang
<!-- repo: sgl-project/sglang -->

#### What it is
LLM serving framework with a focus on structured generation, RadixAttention KV cache reuse, and fast constrained decoding. Strong on agentic/structured workloads.

#### When to reach for it
- High-concurrency structured outputs (JSON, grammars).
- Agent workloads with shared prompt prefixes — RadixAttention shines.

#### When not to
- General-purpose chat-only serving where vLLM's ecosystem and tooling are deeper.

#### How it fits with other tools
Competes with vLLM and TGI on serving; often outperforms on prefix-heavy workloads.

#### Sources
- Repo: https://github.com/sgl-project/sglang
<!-- END TOOL: sgl-project/sglang -->
