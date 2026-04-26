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
Lightpanda: a headless browser written from scratch in Zig (not a Chromium fork) designed for AI and automation. Speaks CDP, so Puppeteer/Playwright clients connect unchanged.

#### When to reach for it
- High-volume crawling/scraping where memory and per-page latency dominate cost — swap it in as the CDP endpoint behind Browser-Use or any Playwright script to collapse the resource footprint of headless Chrome.

#### When not to
- Anything that needs full web-platform fidelity (complex SPAs, CORS, niche Web APIs) — Lightpanda is still in beta with partial coverage; fall back to Steel Browser or plain headless Chrome driven by Browser-Use.

#### Sources
- Repo: https://github.com/lightpanda-io/browser
<!-- END TOOL: lightpanda-io/browser -->

<!-- BEGIN TOOL: Skyvern-AI/skyvern -->
### skyvern
<!-- repo: Skyvern-AI/skyvern -->

#### What it is
Playwright extension that adds vision-LLM-driven `act/extract/validate` primitives plus a no-code workflow builder, with managed cloud (CAPTCHA solvers, proxies) on top.

#### When to reach for it
- Long-tail RPA-shaped workflows across many unfamiliar sites (insurance quoting, government portals, vendor onboarding) where vision-based reasoning beats DOM selectors and where non-engineers need to author the flows.

#### When not to
- A developer-first programmatic agent in code — Browser-Use (Python) or Stagehand (TS) give a tighter feedback loop without the workflow-builder surface area.

#### Sources
- Repo: https://github.com/Skyvern-AI/skyvern
<!-- END TOOL: Skyvern-AI/skyvern -->

<!-- BEGIN TOOL: alibaba/page-agent -->
### page-agent
<!-- repo: alibaba/page-agent -->

#### What it is
Embeddable in-page JavaScript agent that drives the user's own DOM via text-based extraction (no screenshots, no headless browser, no backend). Bring-your-own-LLM, with an optional Chrome extension and MCP server for multi-page reach.

#### When to reach for it
- Shipping an in-product AI copilot that drives the existing web UI of a SaaS/ERP/CRM — drop in a `<script>` tag and turn multi-click flows into one prompt without rewriting the backend or running a server-side browser.

#### When not to
- Server-side automation, scraping, or any task that needs to run without a real user's browser tab — the project explicitly disclaims that shape; reach for Browser-Use or Stagehand instead.

#### Sources
- Repo: https://github.com/alibaba/page-agent
<!-- END TOOL: alibaba/page-agent -->

<!-- BEGIN TOOL: pinchtab/pinchtab -->
### pinchtab
<!-- repo: pinchtab/pinchtab -->

#### What it is
Small Go daemon that exposes a local HTTP/MCP control plane over Chrome, with named profiles, headed/headless instances, and accessibility-tree extraction tuned for token efficiency.

#### When to reach for it
- A single-user, local-first browser runtime an agent on your machine can share — when you want one persistent Chrome with logged-in profiles addressable from CLI, MCP, or curl, instead of spawning a new Playwright per task.

#### When not to
- Multi-tenant or hosted browser-as-a-service deployments — PinchTab is explicit that it is not designed for public-internet exposure; use Steel Browser or a managed offering for that shape.

#### Sources
- Repo: https://github.com/pinchtab/pinchtab
<!-- END TOOL: pinchtab/pinchtab -->

<!-- BEGIN TOOL: steel-dev/steel-browser -->
### steel-browser
<!-- repo: steel-dev/steel-browser -->

#### What it is
Self-hostable browser-as-a-service: a Dockerized Chrome sandbox exposing a REST API and CDP endpoint, with built-in session management, proxy rotation, stealth, and extension support. The open-source counterpart to Browserbase.

#### When to reach for it
- The infrastructure layer underneath an agent framework — when you've already picked Browser-Use or Stagehand and need durable sessions, IP rotation, and one-shot conversion endpoints (markdown/PDF/screenshot) without building the browser pool yourself.

#### When not to
- The agent loop itself — Steel is the runtime, not the brain; pair it with Browser-Use or Stagehand rather than expecting it to plan or extract on its own.

#### Sources
- Repo: https://github.com/steel-dev/steel-browser
<!-- END TOOL: steel-dev/steel-browser -->

<!-- BEGIN TOOL: jo-inc/camofox-browser -->
### camofox-browser
<!-- repo: jo-inc/camofox-browser -->

#### What it is
REST/MCP server wrapping Camoufox (a Firefox fork that spoofs fingerprints at the C++ level), serving accessibility snapshots with stable element refs, search macros, and per-session isolation tuned for agent token budgets.

#### When to reach for it
- Reaching sites that aggressively fingerprint or block automated browsers (Cloudflare, Google, social platforms) where stealth-plugin-on-Chrome stacks have started losing — the C++-level patches sit below anything JS-level detectors can probe.

#### When not to
- Sites you can already reach with vanilla headless Chrome — the stealth premium isn't free (Firefox-only, ~300MB Camoufox download, slower than Chromium); use Steel Browser or Browser-Use on stock Chrome instead.

#### Sources
- Repo: https://github.com/jo-inc/camofox-browser
<!-- END TOOL: jo-inc/camofox-browser -->
