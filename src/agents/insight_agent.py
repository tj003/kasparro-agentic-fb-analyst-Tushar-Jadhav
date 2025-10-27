"""
Insight Agent: Generates hypotheses explaining performance changes.
"""

import json
from typing import Dict, Any, List
from loguru import logger


class InsightAgent:
    """
    Business Insight Specialist that hypothesizes root causes for performance issues.
    """
    
    def __init__(self, llm):
        self.llm = llm
        self.role = "Business Insight Specialist"
        self.goal = "Hypothesize root causes for performance changes"
        self.backstory = """Marketing consultant with expertise in diagnosing 
        campaign performance issues and identifying optimization opportunities."""
    
    def generate_insights(self, data_summary: Dict[str, Any], query: str) -> Dict[str, Any]:
        """
        Generate hypotheses explaining the performance changes.
        
        Args:
            data_summary: Summary from Data Agent
            query: Original business query
            
        Returns:
            Dictionary with hypotheses and insights
        """
        logger.info("Insight Agent generating hypotheses")
        
        # Read the insight prompt
        try:
            with open("../prompts/insight_prompt.md", "r") as f:
                system_prompt = f.read()
        except FileNotFoundError:
            try:
                with open("prompts/insight_prompt.md", "r") as f:
                    system_prompt = f.read()
            except FileNotFoundError:
                logger.warning("Insight prompt file not found, using default")
                system_prompt = "You are a business insight specialist."
        
        # Build the analysis prompt
        user_prompt = f"""
        Analyze the following data and generate insights:
        
        Query: {query}
        
        Data Summary:
        {json.dumps(data_summary, indent=2)}
        
        Generate structured hypotheses about what's causing performance issues.
        Return JSON with hypotheses array, primary_cause, and recommended_actions.
        """
        
        try:
            response = self.llm.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )
            
            insights = self._parse_response(response)
            
            # Validate confidence levels
            insights = self._validate_insights(insights)
            
            logger.info(f"Generated {len(insights.get('hypotheses', []))} hypotheses")
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return self._default_insights(data_summary)
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured insights."""
        response = response.strip()
        
        # Extract JSON from markdown if present
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].split("```")[0].strip()
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.warning("Failed to parse insights JSON")
            # Try to build a basic structure
            return {
                "hypotheses": [
                    {
                        "id": "hypothesis_1",
                        "title": "Unknown Issue",
                        "description": response[:200],
                        "confidence": 0.5,
                        "severity": "medium"
                    }
                ]
            }
    
    def _validate_insights(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize insight confidence levels."""
        if 'hypotheses' in insights:
            for hypothesis in insights['hypotheses']:
                # Ensure confidence is a float between 0 and 1
                if 'confidence' in hypothesis:
                    confidence = hypothesis['confidence']
                    if isinstance(confidence, str):
                        # Try to extract number from string
                        import re
                        numbers = re.findall(r'\d+\.?\d*', confidence)
                        if numbers:
                            confidence = float(numbers[0]) / 100.0
                        else:
                            confidence = 0.5
                    hypothesis['confidence'] = max(0.0, min(1.0, float(confidence)))
                else:
                    hypothesis['confidence'] = 0.5
        
        return insights
    
    def _default_insights(self, data_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Generate default insights if LLM fails."""
        logger.info("Using default insights")
        
        insights = {
            "hypotheses": [],
            "primary_cause": "data_insufficient",
            "recommended_actions": [
                "Review campaign settings",
                "Check audience targeting",
                "Analyze creative performance"
            ]
        }
        
        # Add hypotheses based on data patterns
        if 'patterns' in data_summary:
            for pattern in data_summary['patterns']:
                insights['hypotheses'].append({
                    "id": f"hyp_{len(insights['hypotheses']) + 1}",
                    "title": pattern,
                    "description": f"Data shows: {pattern}",
                    "confidence": 0.7,
                    "severity": "medium",
                    "evidence": [pattern]
                })
        
        return insights

