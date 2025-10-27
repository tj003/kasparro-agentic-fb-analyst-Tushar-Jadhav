"""
Creative Generator: Generates ad creative suggestions.
"""

import json
from typing import Dict, Any, List
from loguru import logger
import pandas as pd


class CreativeGenerator:
    """
    Creative Strategist that generates compelling ad creatives based on insights.
    """
    
    def __init__(self, llm, df: pd.DataFrame):
        self.llm = llm
        self.df = df
        self.role = "Creative Strategist"
        self.goal = "Generate compelling ad creatives based on insights"
        self.backstory = """Copywriter and creative strategist specializing in 
        high-converting ad messaging for performance marketing."""
    
    def generate_creatives(self, 
                          insights: Dict[str, Any], 
                          validated_insights: Dict[str, Any],
                          num_suggestions: int = 5) -> List[Dict[str, Any]]:
        """
        Generate creative suggestions for underperforming campaigns.
        
        Args:
            insights: Original insights
            validated_insights: Validated insights
            num_suggestions: Number of creative suggestions per campaign
            
        Returns:
            List of creative suggestions
        """
        logger.info("Creative Generator generating suggestions")
        
        # Identify campaigns that need creative refresh
        target_campaigns = self._identify_target_campaigns()
        
        if not target_campaigns:
            logger.info("No campaigns needing creative refresh")
            return []
        
        creatives = []
        
        for campaign_name in target_campaigns[:5]:  # Limit to top 5
            campaign_creatives = self._generate_for_campaign(
                campaign_name, 
                insights,
                validated_insights,
                num_suggestions
            )
            creatives.extend(campaign_creatives)
        
        logger.info(f"Generated {len(creatives)} creative suggestions")
        return creatives
    
    def _identify_target_campaigns(self) -> List[str]:
        """Identify campaigns that need creative refresh (low ROAS, low CTR)."""
        target_campaigns = []
        
        if len(self.df) == 0:
            return target_campaigns
        
        # Find campaigns with poor performance
        if 'roas' in self.df.columns and 'campaign_name' in self.df.columns:
            avg_roas_by_campaign = self.df.groupby('campaign_name')['roas'].mean()
            low_performers = avg_roas_by_campaign[
                avg_roas_by_campaign < self.df['roas'].quantile(0.25)
            ]
            target_campaigns = low_performers.index.tolist()
        
        return target_campaigns
    
    def _generate_for_campaign(self,
                               campaign_name: str,
                               insights: Dict[str, Any],
                               validated_insights: Dict[str, Any],
                               num_suggestions: int) -> List[Dict[str, Any]]:
        """Generate creatives for a specific campaign."""
        
        # Get existing creative for context
        campaign_data = self.df[self.df['campaign_name'] == campaign_name]
        existing_creatives = campaign_data['creative_message'].unique().tolist()[:3]
        
        # Read the creative prompt
        try:
            with open("../prompts/creative_prompt.md", "r") as f:
                system_prompt = f.read()
        except FileNotFoundError:
            try:
                with open("prompts/creative_prompt.md", "r") as f:
                    system_prompt = f.read()
            except FileNotFoundError:
                logger.warning("Creative prompt file not found")
                system_prompt = "You are a creative strategist."
        
        # Build the generation prompt
        user_prompt = f"""
        Generate {num_suggestions} new creative ideas for this campaign:
        
        Campaign: {campaign_name}
        
        Existing Creatives:
        {json.dumps(existing_creatives, indent=2)}
        
        Insights:
        {json.dumps(insights.get('hypotheses', []), indent=2)}
        
        Performance Issues: {validated_insights.get('recommendation', {}).get('action', 'General optimization')}
        
        Generate new headline and message combinations that address the issues.
        """
        
        try:
            response = self.llm.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )
            
            parsed_creatives = self._parse_response(response, campaign_name)
            return parsed_creatives
            
        except Exception as e:
            logger.error(f"Error generating creatives: {e}")
            return self._default_creatives(campaign_name, num_suggestions)
    
    def _parse_response(self, response: str, campaign_name: str) -> List[Dict[str, Any]]:
        """Parse LLM response into creative suggestions."""
        response = response.strip()
        
        # Extract JSON from markdown if present
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].split("```")[0].strip()
        
        try:
            data = json.loads(response)
            
            # Handle different response formats
            if 'creatives' in data:
                creatives = data['creatives']
            elif isinstance(data, list):
                creatives = data
            else:
                creatives = [data]
            
            # Ensure all have campaign name
            for creative in creatives:
                creative['campaign_name'] = campaign_name
                if 'id' not in creative:
                    creative['id'] = f"{campaign_name}_{len(creatives)}"
            
            return creatives
            
        except json.JSONDecodeError:
            logger.warning("Failed to parse creatives JSON")
            return self._default_creatives(campaign_name, 3)
    
    def _default_creatives(self, campaign_name: str, num: int) -> List[Dict[str, Any]]:
        """Generate default creative suggestions if LLM fails."""
        logger.info(f"Using default creatives for {campaign_name}")
        
        # Get existing creative for inspiration
        campaign_data = self.df[self.df['campaign_name'] == campaign_name]
        existing = campaign_data['creative_message'].iloc[0] if len(campaign_data) > 0 else "No creative available"
        
        angles = [
            "Value Proposition",
            "Urgency-Based",
            "Benefit-Focused",
            "Problem-Solution",
            "Social Proof"
        ]
        
        creatives = []
        for i, angle in enumerate(angles[:num]):
            creatives.append({
                "id": f"{campaign_name}_creative_{i+1}",
                "campaign_name": campaign_name,
                "angle": angle,
                "headline": f"{angle} - Campaign Headline",
                "message": f"Based on existing creative: {existing[:100]}... Our new angle: {angle}",
                "target_ctr": "2.0-3.0%",
                "rationale": f"Testing {angle.lower()} approach for better engagement"
            })
        
        return creatives

