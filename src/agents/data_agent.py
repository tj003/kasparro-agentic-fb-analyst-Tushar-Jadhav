"""
Data Agent: Summarizes dataset and identifies key patterns.
"""

import pandas as pd
from typing import Dict, Any, List
from loguru import logger
import json


class DataAgent:
    """
    Data Analyst that processes and summarizes marketing campaign data.
    """
    
    def __init__(self, llm):
        self.llm = llm
        self.role = "Data Analyst"
        self.goal = "Summarize dataset characteristics and identify patterns"
        self.backstory = """Data scientist specializing in marketing performance 
        metrics and statistical analysis."""
    
    def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze the dataset and generate summary statistics.
        
        Args:
            df: DataFrame with campaign data
            
        Returns:
            Dictionary with data summary
        """
        logger.info(f"Data Agent analyzing {len(df)} rows")
        
        summary = {
            "total_campaigns": len(df['campaign_name'].unique()),
            "total_records": len(df),
            "date_range": {
                "start": df['date'].min() if 'date' in df.columns else "N/A",
                "end": df['date'].max() if 'date' in df.columns else "N/A"
            },
            "metrics": self._calculate_metrics(df),
            "patterns": self._identify_patterns(df),
            "outliers": self._find_outliers(df)
        }
        
        logger.info("Data analysis complete")
        return summary
    
    def _calculate_metrics(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate summary statistics for key metrics."""
        metrics = {}
        
        if 'roas' in df.columns:
            metrics['roas'] = {
                "mean": float(df['roas'].mean()),
                "median": float(df['roas'].median()),
                "std": float(df['roas'].std()),
                "min": float(df['roas'].min()),
                "max": float(df['roas'].max())
            }
        
        if 'ctr' in df.columns:
            metrics['ctr'] = {
                "mean": float(df['ctr'].mean()),
                "median": float(df['ctr'].median()),
                "std": float(df['ctr'].std())
            }
        
        if 'spend' in df.columns:
            metrics['spend'] = {
                "total": float(df['spend'].sum()),
                "mean": float(df['spend'].mean()),
                "median": float(df['spend'].median())
            }
        
        return metrics
    
    def _identify_patterns(self, df: pd.DataFrame) -> List[str]:
        """Identify patterns in the data."""
        patterns = []
        
        # Check for declining ROAS over time
        if 'date' in df.columns and 'roas' in df.columns:
            df_sorted = df.sort_values('date')
            if len(df_sorted) > 10:
                recent_roas = df_sorted.tail(len(df_sorted) // 4)['roas'].mean()
                early_roas = df_sorted.head(len(df_sorted) // 4)['roas'].mean()
                
                if recent_roas < early_roas * 0.8:
                    patterns.append("Declining ROAS trend detected")
        
        # Check for low-performing campaigns
        if 'roas' in df.columns:
            low_performers = len(df[df['roas'] < 2.0])
            if low_performers > len(df) * 0.3:
                patterns.append(f"{low_performers} campaigns with ROAS < 2.0")
        
        # Check for high spend low performance
        if 'spend' in df.columns and 'roas' in df.columns:
            high_spend_low_roas = df[(df['spend'] > df['spend'].quantile(0.75)) & 
                                    (df['roas'] < 2.0)]
            if len(high_spend_low_roas) > 0:
                patterns.append(f"{len(high_spend_low_roas)} high-spend campaigns with low ROAS")
        
        return patterns
    
    def _find_outliers(self, df: pd.DataFrame) -> Dict[str, List[Dict[str, Any]]]:
        """Identify outliers in the dataset."""
        outliers = {}
        
        if 'roas' in df.columns:
            q1 = df['roas'].quantile(0.25)
            q3 = df['roas'].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            outlier_df = df[(df['roas'] < lower_bound) | (df['roas'] > upper_bound)]
            
            outliers['roas'] = [
                {
                    "campaign": row['campaign_name'],
                    "value": float(row['roas']),
                    "type": "high" if row['roas'] > upper_bound else "low"
                }
                for _, row in outlier_df.iterrows()
            ]
        
        return outliers
    
    def get_campaign_details(self, df: pd.DataFrame, campaign_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific campaign."""
        campaign_data = df[df['campaign_name'] == campaign_name]
        
        if len(campaign_data) == 0:
            return {"error": f"Campaign '{campaign_name}' not found"}
        
        return {
            "campaign_name": campaign_name,
            "record_count": len(campaign_data),
            "avg_roas": float(campaign_data['roas'].mean()),
            "avg_ctr": float(campaign_data['ctr'].mean()),
            "total_spend": float(campaign_data['spend'].sum()),
            "creative_samples": campaign_data['creative_message'].unique().tolist()[:3]
        }


