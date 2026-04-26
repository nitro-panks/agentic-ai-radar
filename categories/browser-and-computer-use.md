---
category: browser-and-computer-use
tools:
  - { name: "Browser-Use", repo: "browser-use/browser-use" }
  - { name: "Stagehand",   repo: "browserbase/stagehand" }
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
