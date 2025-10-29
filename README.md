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
Place the full CSV locally and set the environment variable `DATA_CSV=/path/to/your/full_dataset.csv` to use your complete dataset. A sample CSV with 100-200 rows is included in `data/sample_fb_ads.csv` for testing purposes.

Example usage with environment variable:
```bash
# Linux/Mac
export DATA_CSV=/path/to/your/full_dataset.csv
python src/run.py "Analyze ROAS drop in last 7 days"

# Windows
set DATA_CSV=D:\path\to\your\full_dataset.csv
python src/run.py "Analyze ROAS drop in last 7 days"
```

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

## Sample Evaluator Output

```json
{
  "validated_hypotheses": [
    {
      "hypothesis_id": "h1",
      "title": "Creative fatigue in top-performing ad sets with 15% CTR drop",
      "validation_score": 0.82,
      "metrics": {
        "ctr_change": "-15.3%",
        "impression_change": "+2.1%",
        "affected_campaigns": 2
      },
      "is_valid": true,
      "strength": "strong"
    },
    {
      "hypothesis_id": "h2",
      "title": "Audience overlap causing 22% higher CPM in key segments",
      "validation_score": 0.75,
      "metrics": {
        "cpm_change": "+22.4%",
        "audience_overlap": "35%",
        "affected_campaigns": 3
      },
      "is_valid": true,
      "strength": "medium"
    }
  ],
  "validation_confidence": 0.78,
  "recommendation": {
    "priority_actions": [
      "Refresh creative assets in campaigns with CTR drop",
      "Adjust audience targeting to reduce overlap"
    ]
  }
}
```

## Release

Tag: `v1.0` - [Kasparro Agentic Facebook Analyst v1.0](https://github.com/user/kasparro-agentic-fb-analyst/releases/tag/v1.0)

GitHub release workflow:
```bash
git tag -a v1.0 -m "Initial release: Agentic Facebook Performance Analyst"
git push origin v1.0
```
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

