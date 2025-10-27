# Kasparro — Agentic Facebook Performance Analyst

Production-style agentic AI system for analyzing Facebook Ads performance, diagnosing ROAS changes, and generating creative recommendations using CrewAI and Gemma (via Groq API).

## Quick Start

```bash
python -V  # should be >= 3.10
python -m venv .venv && source .venv/bin/activate  # win: .venv\Scripts\activate
pip install -r requirements.txt
python src/run.py "Analyze ROAS drop in last 7 days"
```

## Data
Place the full CSV locally and set `DATA_CSV=/path/to/synthetic_fb_ads_undergarments.csv` or copy a small sample to `data/sample_fb_ads.csv`. See `data/README.md` for details.

Required columns:
- `campaign_name`
- `creative_message`
- `roas` (Return on Ad Spend)
- `ctr` (Click-Through Rate)
- `spend`
- `impressions`
- `clicks`
- `date`

## Config
Edit `config/config.yaml`:

```yaml
api:
  provider: "groq"
  model: "gemma2-9b-it"
  temperature: 0.7

thresholds:
  roas_low: 2.0
  ctr_low: 0.02
  confidence_threshold: 0.6
```

## Architecture

```
User Query
    ↓
Planner Agent (decomposes query into tasks)
    ↓
    ├──→ Data Agent (summarizes dataset)
    │
    ├──→ Insight Agent (hypothesizes causes)
    │
    ├──→ Evaluator Agent (validates with metrics)
    │
    └──→ Creative Generator (suggests new creatives)
    ↓
Structured Outputs (JSON + Markdown reports)
```


## Repo Map

- `src/agents/` - planner_agent.py, data_agent.py, insight_agent.py, evaluator_agent.py, creative_generator.py
- `src/orchestrator.py` - Main pipeline coordinator
- `src/llm_wrapper.py` - Groq API wrapper
- `src/run.py` - CLI entry point
- `prompts/` - *.md prompt files with variable placeholders
- `reports/` - report.md, insights.json, creatives.json
- `logs/` - JSON traces
- `data/` - sample_fb_ads.csv (auto-generated if missing)

## Run

```bash
python src/run.py "Analyze ROAS drop"
```

Or specify data path:
```bash
python src/run.py "Analyze ROAS drop" --data path/to/your/data.csv
```

## Outputs

- `reports/report.md` - Human-readable summary with insights
- `reports/insights.json` - Structured hypotheses and validation
- `reports/creatives.json` - Generated creative suggestions
- `logs/agent_logs.json` - Full execution trace

## Observability

Include Langfuse screenshots or JSON logs in `reports/observability/`.

## Release

Tag: `v1.0` and paste link here.

GitHub release workflow:
```bash
git tag -a v1.0 -m "Initial release: Agentic Facebook Performance Analyst"
git push origin v1.0
```

## Self-Review

Link to PR describing design choices and tradeoffs.

## Features

- Multi-Agent Reasoning: CrewAI orchestrates specialized agents
- LLM-Powered: Uses Gemma 2-9B via Groq for fast inference
- Data-Driven: Quantitative validation of hypotheses
- Reflection & Retry: Low-confidence outputs trigger refinement
- Production-Ready: Modular, logged, structured outputs

