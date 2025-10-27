"""
Planner Agent: Decomposes high-level queries into specific analysis tasks.
"""

import json
from typing import List, Dict, Any
from loguru import logger
from pydantic import BaseModel


class Task(BaseModel):
    """Represents a single analysis task."""
    id: str
    agent: str
    description: str
    dependencies: List[str] = []


class PlannerAgent:
    """
    Strategic Marketing Planner that breaks down business questions into actionable tasks.
    """
    
    def __init__(self, llm):
        self.llm = llm
        self.role = "Strategic Marketing Planner"
        self.goal = "Decompose analysis requests into actionable tasks"
        self.backstory = """Expert in marketing analytics with 10+ years experience 
        breaking down complex business questions into data-driven analyses."""
    
    def plan(self, query: str, context: Dict[str, Any] = None) -> List[Task]:
        """
        Break down a query into specific tasks.
        
        Args:
            query: The business question/request
            context: Optional additional context
            
        Returns:
            List of Task objects
        """
        logger.info(f"Planner received query: {query}")
        
        # Read the planner prompt
        try:
            with open("../prompts/planner_prompt.md", "r") as f:
                system_prompt = f.read()
        except FileNotFoundError:
            try:
                with open("prompts/planner_prompt.md", "r") as f:
                    system_prompt = f.read()
            except FileNotFoundError:
                logger.warning("Planner prompt file not found, using default")
                system_prompt = "You are a strategic marketing planner."
        
        # Build the task prompt
        user_prompt = f"""
        Business Query: {query}
        
        Context: {context if context else 'No additional context provided'}
        
        Break this query into specific, actionable tasks for data analysis.
        Return a JSON object with the 'tasks' array.
        """
        
        try:
            # Call LLM to generate task plan
            response = self.llm.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )
            
            # Parse the response (should be JSON)
            task_plan = self._parse_response(response)
            
            # Convert to Task objects
            tasks = [Task(**task_data) for task_data in task_plan.get("tasks", [])]
            
            logger.info(f"Generated {len(tasks)} tasks")
            return tasks
            
        except Exception as e:
            logger.error(f"Error in planner: {e}")
            # Return default task plan
            return self._default_tasks(query)
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into task plan."""
        # Try to extract JSON from the response
        response = response.strip()
        
        # Remove markdown code blocks if present
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].split("```")[0].strip()
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON, attempting to extract")
            # Fallback: try to find JSON-like structures
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            raise
    
    def _default_tasks(self, query: str) -> List[Task]:
        """Generate default task plan if LLM fails."""
        logger.info("Using default task plan")
        return [
            Task(
                id="data_summary",
                agent="data_agent",
                description="Summarize dataset characteristics and identify patterns",
                dependencies=[]
            ),
            Task(
                id="insights",
                agent="insight_agent",
                description="Generate hypotheses explaining performance changes",
                dependencies=["data_summary"]
            ),
            Task(
                id="evaluation",
                agent="evaluator_agent",
                description="Validate hypotheses with quantitative metrics",
                dependencies=["insights"]
            ),
            Task(
                id="creatives",
                agent="creative_agent",
                description="Generate creative recommendations for underperformers",
                dependencies=["evaluation"]
            )
        ]

