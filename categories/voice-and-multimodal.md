---
category: voice-and-multimodal
tools:
  - { name: "Pipecat",        repo: "pipecat-ai/pipecat" }
  - { name: "LiveKit Agents", repo: "livekit/agents" }
last_reviewed: 2026-04-26
---

# Voice and Multimodal

## Overview
Real-time voice (and increasingly video) agents. Latency budgets are the defining constraint: STT → LLM → TTS round-trip under ~500ms for natural turn-taking.

## Decision heuristics
- Need a Python pipeline framework with provider plugins → Pipecat.
- WebRTC-native voice/video with LiveKit infra → LiveKit Agents.
- Phone-first agents → Vocode / Vapi (not yet expanded here).

## Tools

<!-- BEGIN TOOL: pipecat-ai/pipecat -->
### Pipecat
<!-- repo: pipecat-ai/pipecat -->

#### What it is
Real-time voice + multimodal agent framework. Pipelines for STT → LLM → TTS with WebRTC transports.

#### When to reach for it
- Phone or voice agents with low-latency turn-taking.

#### When not to
- Async/batched voice — overkill.

#### Sources
- Repo: https://github.com/pipecat-ai/pipecat
<!-- END TOOL: pipecat-ai/pipecat -->

<!-- BEGIN TOOL: livekit/agents -->
### LiveKit Agents
<!-- repo: livekit/agents -->

#### What it is
Agent framework on top of LiveKit's WebRTC stack. Realtime voice/video agents with provider plugins.

#### When to reach for it
- You're already using or want to use LiveKit for media transport.

#### When not to
- You don't need WebRTC — Pipecat's transport options are broader.

#### Sources
- Repo: https://github.com/livekit/agents
<!-- END TOOL: livekit/agents -->
