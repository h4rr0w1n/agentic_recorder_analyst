"""
Main entry point for the Aviation AI Solution.

This module provides the command-line interface and main execution logic
for running the multi-agent aviation analysis system.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from .agents.orchestrator_agent import OrchestratorAgent


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    try:
        import yaml
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except ImportError:
        # Fallback to simple JSON config if PyYAML not available
        json_path = config_path.replace('.yaml', '.json')
        if Path(json_path).exists():
            with open(json_path, 'r') as f:
                return json.load(f)
        return {}
    except FileNotFoundError:
        print(f"Warning: Config file {config_path} not found. Using defaults.")
        return {}


def process_directory(input_dir: str, orchestrator: OrchestratorAgent) -> Dict[str, Any]:
    """Process all files in an input directory."""
    results = []
    input_path = Path(input_dir)
    
    if not input_path.exists():
        return {"error": f"Input directory {input_dir} does not exist"}
    
    # Find all relevant files
    file_patterns = ['*.json', '*.txt', '*.csv', '*.log']
    files = []
    for pattern in file_patterns:
        files.extend(input_path.glob(f'**/{pattern}'))
    
    print(f"Found {len(files)} files to process")
    
    for file_path in files:
        try:
            # Extract flight code from filename or content
            flight_code = file_path.stem.split('_')[0] if '_' in file_path.stem else None
            
            # Read file content
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Process based on file type
            if file_path.suffix == '.json':
                data = json.loads(content)
                flight_code = flight_code or data.get('flight_code')
            else:
                data = {"content": content, "source": str(file_path)}
            
            # Run analysis workflow
            result = orchestrator.execute_task({
                "task_type": "analyze_flight",
                "flight_code": flight_code,
                "data": data
            })
            
            results.append({
                "file": str(file_path),
                "flight_code": flight_code,
                "result": result,
                "processed_at": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            results.append({
                "file": str(file_path),
                "error": str(e),
                "processed_at": datetime.utcnow().isoformat()
            })
    
    return {"files_processed": len(results), "results": results}


def process_stream(stream_url: str, orchestrator: OrchestratorAgent) -> Dict[str, Any]:
    """Process data from a streaming source."""
    print(f"Processing stream from: {stream_url}")
    
    # In production, this would connect to actual streaming sources
    # For now, simulate with sample data
    
    sample_stream_data = [
        {"timestamp": "2026-05-06T14:30:00Z", "type": "adsb", "flight": "DLH456", "altitude": 35000},
        {"timestamp": "2026-05-06T14:30:05Z", "type": "metar", "station": "EDDF", "visibility": 9999},
        {"timestamp": "2026-05-06T14:30:10Z", "type": "atc_transcript", "text": "DLH456 cleared to descend"},
    ]
    
    result = orchestrator.execute_task({
        "task_type": "real_time_monitoring",
        "stream_data": sample_stream_data
    })
    
    return result


def run_analysis(flight_code: str, orchestrator: OrchestratorAgent, 
                 time_window: Optional[str] = None, fir: Optional[str] = None) -> Dict[str, Any]:
    """Run analysis for a specific flight."""
    print(f"Analyzing flight: {flight_code}")
    
    task = {
        "task_type": "analyze_flight",
        "flight_code": flight_code
    }
    
    if time_window:
        task["time_window"] = {"start": time_window.split(',')[0], "end": time_window.split(',')[1]}
    if fir:
        task["fir"] = fir
    
    result = orchestrator.execute_task(task)
    return result


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Aviation AI Solution - Multi-Agent Analysis System"
    )
    
    parser.add_argument(
        "--config", "-c",
        default="config/config.yaml",
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--input", "-i",
        help="Input directory containing aviation records"
    )
    
    parser.add_argument(
        "--stream-url", "-s",
        help="URL for streaming data source"
    )
    
    parser.add_argument(
        "--flight", "-f",
        help="Flight code to analyze (e.g., DLH456)"
    )
    
    parser.add_argument(
        "--time-window", "-t",
        help="Time window for analysis (start,end)"
    )
    
    parser.add_argument(
        "--fir",
        help="Flight Information Region (e.g., EDGG)"
    )
    
    parser.add_argument(
        "--output", "-o",
        default="./output",
        help="Output directory for results"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Initialize orchestrator
    print("Initializing Aviation AI System...")
    orchestrator = OrchestratorAgent(config=config)
    
    if not orchestrator.initialize():
        print("ERROR: Failed to initialize system")
        sys.exit(1)
    
    print("System initialized successfully")
    print("=" * 60)
    
    try:
        # Determine which mode to run
        if args.input:
            # Process directory
            print(f"\nProcessing directory: {args.input}")
            results = process_directory(args.input, orchestrator)
            
        elif args.stream_url:
            # Process stream
            print(f"\nProcessing stream: {args.stream_url}")
            results = process_stream(args.stream_url, orchestrator)
            
        elif args.flight:
            # Analyze specific flight
            print(f"\nAnalyzing flight: {args.flight}")
            results = run_analysis(args.flight, orchestrator, args.time_window, args.fir)
            
        else:
            # Demo mode with sample data
            print("\nRunning demo analysis...")
            results = run_analysis("DLH456", orchestrator, fir="EDGG")
        
        # Save results
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\nResults saved to: {output_file}")
        
        # Print summary
        if isinstance(results, dict):
            print("\n" + "=" * 60)
            print("ANALYSIS SUMMARY")
            print("=" * 60)
            
            if "output" in results:
                summary = results["output"].get("summary", {})
                print(f"Flight: {summary.get('flight_code', 'N/A')}")
                print(f"Risk Level: {summary.get('risk_level', 'N/A')}")
                print(f"Risk Score: {summary.get('risk_score', 0):.3f}")
                print(f"Priority: {summary.get('priority', 'routine')}")
                
                recommendations = results["output"].get("recommendations", [])
                if recommendations:
                    print(f"\nRecommendations ({len(recommendations)}):")
                    for i, rec in enumerate(recommendations[:3], 1):
                        print(f"  {i}. [{rec.get('priority', 'routine')}] {rec.get('text', '')[:80]}")
            
            print("=" * 60)
        
        return 0
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
        
    finally:
        # Cleanup
        orchestrator.shutdown()
        print("\nSystem shutdown complete")


if __name__ == "__main__":
    sys.exit(main())
