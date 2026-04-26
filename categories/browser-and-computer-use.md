---
category: browser-and-computer-use
tools:
  - { name: "Browser-Use", repo: "browser-use/browser-use" }
  - { name: "Stagehand",   repo: "browserbase/stagehand" }
  - { name: "browser", repo: "lightpanda-io/browser" }
  - { name: "skyvern", repo: "Skyvern-AI/skyvern" }
  - { name: "page-agent", repo: "alibaba/page-agent" }
  - { name: "pinchtab", repo: "pinchtab/pinchtab" }
  - { name: "steel-browser", repo: "steel-dev/steel-browser" }
  - { name: "camofox-browser", repo: "jo-inc/camofox-browser" }
last_reviewed: 2026-04-26
---

# Browser and Computer Use

## Overview
Letting LLMs drive browsers (and increasingly desktops). DOM extraction, vision, and an action vocabulary tuned for model context windows. Distinct from straight Playwright by virtue of the model-in-the-loop control surface.

## Decision heuristics
- Python stack, want autonomous DOM-aware navigation → Browser-Use.
- TypeScript stack, want deterministic Playwright code with surgical AI assists → Stagehand.
- Computer-use (full screen) instead of just browser → Anthropic Computer Use reference (not yet expanded here).

## Tools

<!-- BEGIN TOOL: browser-use/browser-use -->
### Browser-Use
<!-- repo: browser-use/browser-use -->

#### What it is
Library for letting LLMs drive a real browser via Playwright. DOM extraction tuned for LLM context, action primitives.

#### When to reach for it
- Web automation/scraping jobs where DOM is dynamic and a vision-or-DOM-aware agent helps.

#### When not to
- Static sites — plain Playwright or a scraper is cheaper.

#### Sources
- Repo: https://github.com/browser-use/browser-use
<!-- END TOOL: browser-use/browser-use -->

<!-- BEGIN TOOL: browserbase/stagehand -->
### Stagehand
<!-- repo: browserbase/stagehand -->

#### What it is
TS browser automation that mixes Playwright code with `act/extract/observe` LLM primitives. From Browserbase.

#### When to reach for it
- TypeScript stack, want deterministic Playwright code with surgical AI assists.

#### When not to
- Python — Browser-Use is the natural fit.

#### Sources
- Repo: https://github.com/browserbase/stagehand
<!-- END TOOL: browserbase/stagehand -->

<!-- BEGIN TOOL: lightpanda-io/browser -->
### browser
<!-- repo: lightpanda-io/browser -->

#### What it is
Lightpanda: the headless browser designed for AI and automation

#### When to reach for it
- _TODO — needs human review (auto-triaged stub)._

#### When not to
- _TODO — needs human review (auto-triaged stub)._

#### Triage notes
- Auto-triaged 2026-04-26 (Instructor-scored, confidence 0.85): Lightpanda is a purpose-built headless browser in Zig, explicitly designed for AI and automation. Unlike Browser-Use and Stagehand which wrap Playwright/Puppeteer, it offers a distinctive native implementation optimized for performance. With 29K stars and active development, it's a real infrastructure choice.

#### Sources
- Repo: https://github.com/lightpanda-io/browser
<!-- END TOOL: lightpanda-io/browser -->

<!-- BEGIN TOOL: Skyvern-AI/skyvern -->
### skyvern
<!-- repo: Skyvern-AI/skyvern -->

#### What it is
Automate browser based workflows with AI

#### When to reach for it
- _TODO — needs human review (auto-triaged stub)._

#### When not to
- _TODO — needs human review (auto-triaged stub)._

#### How it fits with other tools
- Possible overlap with: `browser-use/browser-use`, `browserbase/stagehand`

#### Triage notes
- Auto-triaged 2026-04-26 (Instructor-scored, confidence 0.85): Skyvern uses AI vision models to automate browser workflows, distinct from browser-use's API approach and Stagehand's DOM automation. Vision-based interaction makes it resilient to UI changes. 21K+ stars, actively maintained, represents a legitimate alternative approach worth evaluating.

#### Sources
- Repo: https://github.com/Skyvern-AI/skyvern
<!-- END TOOL: Skyvern-AI/skyvern -->

<!-- BEGIN TOOL: alibaba/page-agent -->
### page-agent
<!-- repo: alibaba/page-agent -->

#### What it is
JavaScript in-page GUI agent. Control web interfaces with natural language.

#### When to reach for it
- _TODO — needs human review (auto-triaged stub)._

#### When not to
- _TODO — needs human review (auto-triaged stub)._

#### How it fits with other tools
- Possible overlap with: `browser-use/browser-use`, `browserbase/stagehand`

#### Triage notes
- Auto-triaged 2026-04-26 (Instructor-scored, confidence 0.85): Page-agent offers a distinctive in-page JavaScript approach to browser automation with natural language, contrasting with the Python-based external orchestration of browser-use and Stagehand. This fills a gap for embedded GUI control scenarios. With 17K stars and MIT license, it's established enough to track.

#### Sources
- Repo: https://github.com/alibaba/page-agent
<!-- END TOOL: alibaba/page-agent -->

<!-- BEGIN TOOL: pinchtab/pinchtab -->
### pinchtab
<!-- repo: pinchtab/pinchtab -->

#### What it is
High-performance browser automation bridge and multi-instance orchestrator with advanced stealth injection and real-time dashboard.

#### When to reach for it
- _TODO — needs human review (auto-triaged stub)._

#### When not to
- _TODO — needs human review (auto-triaged stub)._

#### Triage notes
- Auto-triaged 2026-04-26 (Instructor-scored, confidence 0.75): High-performance Go-based browser automation bridge with multi-instance orchestration, stealth injection, and real-time dashboard. Distinct from tracked Python tools (Browser-Use, Stagehand) by targeting production-scale fleet management with advanced evasion. Fills an infrastructure gap for enterprise browser automation.

#### Sources
- Repo: https://github.com/pinchtab/pinchtab
<!-- END TOOL: pinchtab/pinchtab -->

<!-- BEGIN TOOL: steel-dev/steel-browser -->
### steel-browser
<!-- repo: steel-dev/steel-browser -->

#### What it is
🔥 Open Source Browser API for AI Agents & Apps. Steel Browser is a batteries-included browser sandbox that lets you automate the web without worrying about infrastructure.

#### When to reach for it
- _TODO — needs human review (auto-triaged stub)._

#### When not to
- _TODO — needs human review (auto-triaged stub)._

#### How it fits with other tools
- Possible overlap with: `browser-use/browser-use`, `browserbase/stagehand`

#### Triage notes
- Auto-triaged 2026-04-26 (Instructor-scored, confidence 0.82): Steel Browser is a batteries-included browser automation sandbox for AI agents, offering managed infrastructure. It addresses a different sub-shape than Browser-Use and Stagehand: hosted browser infrastructure vs. agent-focused frameworks, solving the operational burden of browser automation at scale.

#### Sources
- Repo: https://github.com/steel-dev/steel-browser
<!-- END TOOL: steel-dev/steel-browser -->

<!-- BEGIN TOOL: jo-inc/camofox-browser -->
### camofox-browser
<!-- repo: jo-inc/camofox-browser -->

#### What it is
Stealth headless browser for AI agents — bypass Cloudflare, bot detection, and anti-scraping. Drop-in Puppeteer/Playwright replacement.

#### When to reach for it
- _TODO — needs human review (auto-triaged stub)._

#### When not to
- _TODO — needs human review (auto-triaged stub)._

#### Triage notes
- Auto-triaged 2026-04-26 (Instructor-scored, confidence 0.85): Stealth browser designed for AI agents with anti-detection capabilities (Cloudflare bypass, bot evasion). Offers a distinct niche from Browser-Use and Stagehand by focusing on stealth-layer infrastructure rather than high-level interaction abstractions.

#### Sources
- Repo: https://github.com/jo-inc/camofox-browser
<!-- END TOOL: jo-inc/camofox-browser -->
