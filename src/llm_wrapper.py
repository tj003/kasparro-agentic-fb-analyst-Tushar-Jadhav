"""
LLM Wrapper for Groq API integration with Gemma model.
"""

import os
from typing import Optional
from loguru import logger
from groq import Groq
import yaml


class GroqLLM:
    """
    Wrapper for Groq API with Gemma model.
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize Groq LLM with configuration."""
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.api_config = self.config.get('api', {})
        self.model = self.api_config.get('model', 'gemma2-9b-it')
        self.temperature = self.api_config.get('temperature', 0.7)
        self.max_tokens = self.api_config.get('max_tokens', 2000)
        
        # Initialize Groq client
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            logger.warning("GROQ_API_KEY not found in environment. Using placeholder.")
            self.client = None
        else:
            try:
                self.client = Groq(api_key=api_key)
                logger.info("Groq client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
                self.client = None
    
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generate a response using the LLM.
        
        Args:
            system_prompt: System prompt for the model
            user_prompt: User prompt/query
            
        Returns:
            Generated response text
        """
        if not self.client:
            logger.warning("Groq client not available, returning mock response")
            return self._mock_generate(system_prompt, user_prompt)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            result = response.choices[0].message.content
            logger.info(f"Generated response ({len(result)} chars)")
            return result
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return self._mock_generate(system_prompt, user_prompt)
    
    def _mock_generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate a mock response when API is unavailable."""
        logger.info("Using mock LLM response")
        
        # Simple heuristic-based mock response
        if "plan" in system_prompt.lower() or "task" in user_prompt.lower():
            return """{
  "tasks": [
    {"id": "task_1", "agent": "data_agent", "description": "Summarize dataset"},
    {"id": "task_2", "agent": "insight_agent", "description": "Generate hypotheses", "dependencies": ["task_1"]},
    {"id": "task_3", "agent": "evaluator_agent", "description": "Validate with metrics", "dependencies": ["task_2"]},
    {"id": "task_4", "agent": "creative_agent", "description": "Generate creative suggestions", "dependencies": ["task_3"]}
  ]
}"""
        
        elif "insight" in system_prompt.lower():
            return """{
  "hypotheses": [
    {
      "id": "hyp_1",
      "title": "Creative Fatigue",
      "description": "Ad creatives showing declining engagement over time",
      "confidence": 0.75,
      "evidence": ["CTR dropped significantly over campaign duration"],
      "severity": "high"
    }
  ],
  "primary_cause": "hyp_1",
  "recommended_actions": [
    "Refresh creative messaging",
    "Test new ad formats"
  ]
}"""
        
        elif "evaluator" in system_prompt.lower():
            return """{
  "validated_hypotheses": [
    {
      "hypothesis_id": "hyp_1",
      "title": "Creative Fatigue",
      "validation_score": 0.82,
      "metrics": {"correlation": -0.75, "p_value": 0.001, "sample_size": 150},
      "is_valid": true,
      "strength": "strong"
    }
  ],
  "recommendation": {
    "action": "Refresh creative",
    "priority": "high",
    "expected_impact": "+15-25% CTR"
  }
}"""
        
        elif "creative" in system_prompt.lower():
            return """{
  "creatives": [
    {
      "angle": "Value-focused",
      "headline": "Save 40% on Premium Quality - Limited Time",
      "message": "Get the best value now! Our biggest sale is ending soon. Shop now and save big.",
      "target_ctr": "2.5-3.5%",
      "rationale": "Clear value prop with urgency"
    }
  ]
}"""
        
        return "Mock response generated successfully."


