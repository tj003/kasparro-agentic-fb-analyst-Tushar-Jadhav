"""
Main Orchestrator for the Kasparro Agentic Facebook Analyst.
Coordinates multiple agents to analyze Facebook Ads performance.
"""

import pandas as pd
import json
import yaml
from datetime import datetime
from typing import Dict, Any, List
from loguru import logger
import os

from llm_wrapper import GroqLLM
from agents.planner_agent import PlannerAgent, Task
from agents.data_agent import DataAgent
from agents.insight_agent import InsightAgent
from agents.evaluator_agent import EvaluatorAgent
from agents.creative_generator import CreativeGenerator


class Orchestrator:
    """
    Main orchestrator for the multi-agent system.
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize orchestrator with configuration."""
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize LLM
        self.llm = GroqLLM(config_path)
        
        # Initialize agents
        self.planner = PlannerAgent(self.llm)
        self.data_agent = DataAgent(self.llm)
        self.insight_agent = InsightAgent(self.llm)
        self.evaluator_agent = None  # Initialize with data
        self.creative_generator = None  # Initialize with data
        
        # Execution log
        self.execution_log = {
            "start_time": datetime.now().isoformat(),
            "query": "",
            "tasks": [],
            "results": {},
            "end_time": None,
            "status": "running"
        }
    
    def analyze(self, query: str, data_path: str = "data/sample_fb_ads.csv") -> Dict[str, Any]:
        """
        Main analysis pipeline.
        
        Args:
            query: Business question/query
            data_path: Path to the data file
            
        Returns:
            Dictionary with analysis results
        """
        logger.info(f"Starting analysis for query: {query}")
        self.execution_log["query"] = query
        self.execution_log["start_time"] = datetime.now().isoformat()
        
        try:
            # Load data
            df = self._load_data(data_path)
            logger.info(f"Loaded {len(df)} records")
            
            # Initialize agents that need data
            self.evaluator_agent = EvaluatorAgent(self.llm, df)
            self.creative_generator = CreativeGenerator(self.llm, df)
            
            # Plan tasks
            tasks = self.planner.plan(query)
            self.execution_log["tasks"] = [task.model_dump() for task in tasks]
            
            results = {}
            
            # Execute tasks
            for task in tasks:
                task_result = self._execute_task(task, df, query)
                results[task.id] = task_result
                self.execution_log["results"][task.id] = task_result
            
            # Compile final report
            report = self._compile_report(query, results, df)
            
            self.execution_log["end_time"] = datetime.now().isoformat()
            self.execution_log["status"] = "completed"
            
            logger.info("Analysis completed successfully")
            return report
            
        except Exception as e:
            logger.error(f"Error in analysis: {e}")
            self.execution_log["status"] = "failed"
            self.execution_log["error"] = str(e)
            raise
    
    def _load_data(self, data_path: str) -> pd.DataFrame:
        """Load and preprocess the data."""
        if not os.path.exists(data_path):
            logger.warning(f"Data file not found: {data_path}. Creating sample data.")
            return self._create_sample_data()
        
        df = pd.read_csv(data_path)
        logger.info(f"Loaded data with columns: {df.columns.tolist()}")
        return df
    
    def _create_sample_data(self) -> pd.DataFrame:
        """Create sample data for testing."""
        import numpy as np
        
        logger.info("Creating sample Facebook Ads data")
        
        campaigns = ["Summer Sale", "Winter Collection", "Spring Promo", "Holiday Special", "New Year"]
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        
        data = []
        for campaign in campaigns:
            for i in range(50):
                date = np.random.choice(dates)
                data.append({
                    'campaign_name': campaign,
                    'date': str(date),
                    'spend': np.random.uniform(50, 500),
                    'impressions': np.random.randint(1000, 10000),
                    'clicks': np.random.randint(20, 300),
                    'ctr': np.random.uniform(0.01, 0.05),
                    'roas': np.random.uniform(1.5, 5.0),
                    'creative_message': f"{campaign} - Amazing deals await! Shop now."
                })
        
        df = pd.DataFrame(data)
        
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        df.to_csv("data/sample_fb_ads.csv", index=False)
        
        logger.info(f"Created sample data with {len(df)} records")
        return df
    
    def _execute_task(self, task: Task, df: pd.DataFrame, query: str) -> Dict[str, Any]:
        """Execute a specific task."""
        logger.info(f"Executing task: {task.id} ({task.agent})")
        
        try:
            if task.agent == "data_agent":
                return self.data_agent.analyze(df)
            
            elif task.agent == "insight_agent":
                # Get data summary first
                data_summary = self.execution_log["results"].get("data_summary", {})
                if not data_summary:
                    data_summary = self.data_agent.analyze(df)
                return self.insight_agent.generate_insights(data_summary, query)
            
            elif task.agent == "evaluator_agent":
                # Get insights first
                insights = self.execution_log["results"].get("insights", {})
                if not insights:
                    data_summary = self.execution_log["results"].get("data_summary", {})
                    insights = self.insight_agent.generate_insights(data_summary, query)
                
                data_summary = self.execution_log["results"].get("data_summary", {})
                return self.evaluator_agent.evaluate(insights, data_summary)
            
            elif task.agent == "creative_agent":
                # Get insights and validations
                insights = self.execution_log["results"].get("insights", {})
                validated = self.execution_log["results"].get("evaluation", {})
                
                if not validated:
                    data_summary = self.execution_log["results"].get("data_summary", {})
                    insights = self.insight_agent.generate_insights(data_summary, query)
                    validated = self.evaluator_agent.evaluate(insights, data_summary)
                
                num_suggestions = self.config.get('creative', {}).get('num_suggestions', 5)
                return self.creative_generator.generate_creatives(insights, validated, num_suggestions)
            
            else:
                logger.warning(f"Unknown agent: {task.agent}")
                return {"status": "unknown_agent", "task": task.model_dump()}
                
        except Exception as e:
            logger.error(f"Error executing task {task.id}: {e}")
            return {"status": "error", "error": str(e), "task": task.model_dump()}
    
    def _compile_report(self, query: str, results: Dict[str, Any], df: pd.DataFrame) -> Dict[str, Any]:
        """Compile final report from all results."""
        
        # Map task results to proper keys
        data_summary = {}
        insights = {}
        validated_insights = {}
        creative_suggestions = []
        
        # Find results by task ID or look for keys
        for key, value in results.items():
            if key.startswith("task_"):
                # This is a task result - need to identify the agent
                if isinstance(value, dict):
                    if "hypotheses" in value:
                        insights = value
                    elif "validated_hypotheses" in value:
                        validated_insights = value
                    elif isinstance(value, list):
                        creative_suggestions = value
                    elif "total_campaigns" in value:
                        data_summary = value
        
        # Also check for direct keys
        if "data_summary" in results:
            data_summary = results["data_summary"]
        if "insights" in results and "hypotheses" in results["insights"]:
            insights = results["insights"]
        if "evaluation" in results:
            validated_insights = results["evaluation"]
        if "creatives" in results:
            creative_suggestions = results["creatives"]
        
        report = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_records": len(df),
                "total_campaigns": len(df['campaign_name'].unique()) if 'campaign_name' in df.columns else 0,
                "analysis_status": "completed"
            },
            "data_summary": data_summary,
            "insights": insights,
            "validated_insights": validated_insights,
            "creative_suggestions": creative_suggestions,
            "recommendations": self._extract_recommendations(validated_insights, insights)
        }
        
        return report
    
    def _extract_recommendations(self, validated_insights: Dict[str, Any] = None, insights: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Extract actionable recommendations from results."""
        recommendations = []
        
        validated_insights = validated_insights or {}
        insights = insights or {}
        
        # From validated insights
        if "recommendation" in validated_insights:
            rec = validated_insights["recommendation"]
            recommendations.append({
                "type": "optimization",
                "action": rec.get("action", "Review campaign performance"),
                "priority": rec.get("priority", "medium"),
                "expected_impact": rec.get("expected_impact", "Positive")
            })
        
        # From insights
        if "recommended_actions" in insights:
            for action in insights["recommended_actions"]:
                recommendations.append({
                    "type": "action",
                    "description": action,
                    "priority": "medium"
                })
        
        return recommendations
    
    def save_results(self, results: Dict[str, Any], output_dir: str = "reports"):
        """Save results to files."""
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        
        # Save insights as JSON
        insights = results.get("insights", {})
        validated = results.get("validated_insights", {})
        insights_json = {
            "hypotheses": insights.get("hypotheses", []) if isinstance(insights, dict) else [],
            "validated": validated
        }
        with open(f"{output_dir}/insights.json", "w") as f:
            json.dump(insights_json, f, indent=2)
        
        # Save creatives as JSON
        creatives_json = results.get("creative_suggestions", [])
        with open(f"{output_dir}/creatives.json", "w") as f:
            json.dump(creatives_json, f, indent=2)
        
        # Save report as markdown
        report_md = self._generate_markdown_report(results)
        with open(f"{output_dir}/report.md", "w") as f:
            f.write(report_md)
        
        # Save execution log
        with open("logs/agent_logs.json", "w") as f:
            json.dump(self.execution_log, f, indent=2)
        
        logger.info(f"Results saved to {output_dir}/")
    
    def _generate_markdown_report(self, results: Dict[str, Any]) -> str:
        """Generate human-readable markdown report."""
        
        md = f"""# Facebook Ads Performance Analysis Report

## Query
{results.get('query', 'N/A')}

**Analysis Date:** {results.get('timestamp', 'N/A')}

---

## Executive Summary

**Total Records Analyzed:** {results.get('summary', {}).get('total_records', 0)}  
**Total Campaigns:** {results.get('summary', {}).get('total_campaigns', 0)}  
**Status:** {results.get('summary', {}).get('analysis_status', 'unknown')}

---

## Key Insights

"""
        
        # Add insights
        insights = results.get("insights", {})
        if "hypotheses" in insights:
            md += "### Performance Hypotheses\n\n"
            for hyp in insights["hypotheses"]:
                md += f"**{hyp.get('title', 'N/A')}** (Confidence: {hyp.get('confidence', 0):.1%})\n"
                md += f"- {hyp.get('description', 'N/A')}\n\n"
        
        # Add validated insights
        validated = results.get("validated_insights", {})
        if "validated_hypotheses" in validated:
            md += "### Validated Insights\n\n"
            for vh in validated["validated_hypotheses"]:
                score = vh.get('validation_score', 0)
                md += f"**{vh.get('title', 'N/A')}** - Validation Score: {score:.1%}\n"
                md += f"- Strength: {vh.get('strength', 'N/A')}\n"
                md += f"- Is Valid: {'Yes' if vh.get('is_valid', False) else 'No'}\n\n"
        
        # Add recommendations
        recommendations = results.get("recommendations", [])
        if recommendations:
            md += "## Recommended Actions\n\n"
            for i, rec in enumerate(recommendations, 1):
                md += f"{i}. **{rec.get('action', rec.get('description', 'N/A'))}**\n"
                md += f"   - Priority: {rec.get('priority', 'medium').upper()}\n"
                md += f"   - Expected Impact: {rec.get('expected_impact', 'Positive')}\n\n"
        
        # Add creative suggestions
        creatives = results.get("creative_suggestions", [])
        if creatives:
            md += "## Creative Suggestions\n\n"
            campaigns = {}
            for creative in creatives:
                campaign = creative.get('campaign_name', 'Unknown')
                if campaign not in campaigns:
                    campaigns[campaign] = []
                campaigns[campaign].append(creative)
            
            for campaign, campaign_creatives in campaigns.items():
                md += f"### {campaign}\n\n"
                for creative in campaign_creatives[:3]:  # Show top 3
                    md += f"**{creative.get('angle', 'Creative')}**\n"
                    md += f"- Headline: {creative.get('headline', 'N/A')}\n"
                    md += f"- Message: {creative.get('message', 'N/A')[:100]}...\n"
                    md += f"- Target CTR: {creative.get('target_ctr', 'N/A')}\n\n"
        
        md += "\n---\n\n*Generated by Kasparro Agentic Facebook Analyst*"
        
        return md

