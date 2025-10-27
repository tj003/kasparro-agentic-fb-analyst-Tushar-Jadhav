"""
Entry point for Kasparro Agentic Facebook Analyst.
"""

import sys
import argparse
import os
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

import sys
sys.path.insert(0, '..' if sys.path[0] != '' else '.')

from orchestrator import Orchestrator

# Fix Windows console encoding
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"


def setup_logging():
    """Configure logging."""
    os.makedirs("logs", exist_ok=True)
    logger.add(
        "logs/app.log",
        rotation="10 MB",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Kasparro Agentic Facebook Analyst"
    )
    parser.add_argument(
        "query",
        type=str,
        nargs="?",
        default="Analyze ROAS drop",
        help="Business query/question to analyze"
    )
    parser.add_argument(
        "--data",
        type=str,
        default="../data/sample_fb_ads.csv",
        help="Path to data file"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="../config/config.yaml",
        help="Path to configuration file"
    )
    
    args = parser.parse_args()
    
    # Setup console and logging
    console = Console(legacy_windows=False, force_terminal=True)
    setup_logging()
    
    # Display banner
    print("\n=== Kasparro Agentic Facebook Analyst ===\n")
    
    print(f"Query: {args.query}")
    print(f"Data: {args.data}\n")
    
    try:
        # Initialize orchestrator
        orchestrator = Orchestrator(args.config)
        
        # Run analysis
        print("Running analysis...")
        results = orchestrator.analyze(args.query, args.data)
        
        # Save results
        print("Saving results...")
        orchestrator.save_results(results)
        
        # Display summary
        print("\n=== Analysis Complete ===\n")
        
        print(f"Records Analyzed: {results.get('summary', {}).get('total_records', 0)}")
        print(f"Campaigns: {results.get('summary', {}).get('total_campaigns', 0)}")
        print(f"Insights Generated: {len(results.get('insights', {}).get('hypotheses', []))}")
        print(f"Creatives Generated: {len(results.get('creative_suggestions', []))}")
        
        print("\nReports saved to:")
        print("   - reports/report.md")
        print("   - reports/insights.json")
        print("   - reports/creatives.json")
        print("   - logs/agent_logs.json")
        
        # Show recommendations
        recommendations = results.get("recommendations", [])
        if recommendations:
            print("\nTop Recommendations:")
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"  {i}. {rec.get('action', rec.get('description', 'N/A'))}")
        
        print("\n")
        
    except Exception as e:
        print(f"\nERROR: {e}\n")
        logger.error(f"Error in main: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

