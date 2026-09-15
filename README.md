# AutoCode Router

A tiny local-first router for Claude Code on macOS/Linux.

It sends routine coding tasks to a local Ollama model and escalates harder work to Claude automatically, so you can stay in one terminal and spend frontier-model capacity only where it matters.

## Why

Claude Code can talk directly to Ollama through the Anthropic-compatible endpoint, but choosing the right backend for every task is still manual. AutoCode adds a lightweight decision layer without running another proxy server.

## Requirements

- Python 3.10+
- Claude Code installed and authenticated
- Ollama installed for local routing
- A local coding model, e.g. `qwen3.5:27b`

## Install

```bash
git clone https://github.com/pierreneuville/DevmobileClaude.git
cd DevmobileClaude
bash install.sh
```

If needed, add `~/.local/bin` to your PATH.

## Use

```bash
autocode "rename this variable and update the test"
```

For a complex task:

```bash
autocode "review the production architecture, find the root cause of the concurrency bug, refactor the affected modules and verify the migration"
```

Inspect the routing decision without running anything:

```bash
autocode "fix this typo" --dry-run
```

Bias toward speed/local inference:

```bash
autocode "implement this endpoint" --mode fast
```

Bias toward quality/frontier inference:

```bash
autocode "review this design" --mode quality
```

Force a route:

```bash
autocode "task" --mode local
autocode "task" --mode cloud
```

Choose another local model:

```bash
autocode "task" --local-model qwen3-coder
```

Or persist it:

```bash
export AUTOCODE_LOCAL_MODEL="qwen3.5:27b"
```

## How routing works

AutoCode assigns a small complexity score from task size and signals such as architecture, security, migrations, debugging, concurrency, repo-wide changes and verification. Tasks below the threshold use Ollama; tasks at or above it use Claude.

The heuristic is intentionally transparent. You can inspect every decision with `--dry-run` or change the threshold:

```bash
autocode "task" --threshold 7 --dry-run
```

## Run tests

```bash
python3 -m unittest -v
```

## Privacy

Local routes point Claude Code at `http://127.0.0.1:11434` and do not intentionally send the prompt to Anthropic. Cloud routes remove the Ollama routing overrides and use your normal Claude Code authentication.

## Status

Early MVP. The next useful layer is evidence-based routing: learn from task outcomes, latency and retries instead of relying only on static heuristics.
