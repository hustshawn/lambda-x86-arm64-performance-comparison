#!/usr/bin/env python3
"""
Production performance testing script for Lambda Performance Comparison.

This script runs comprehensive performance tests against deployed AWS Lambda functions
and provides statistical analysis comparing ARM64 vs x86_64 architectures.
"""

import requests
import json
import time
import statistics
from typing import Dict, List, Any
from datetime import datetime
import argparse
import sys
import os
import subprocess


class PerformanceTester:
    """Production-grade performance testing utility for deployed Lambda functions."""
    
    def __init__(self, arm64_url: str, x86_url: str, verbose: bool = False):
        self.arm64_url = arm64_url
        self.x86_url = x86_url
        self.verbose = verbose
        
    def run_single_test(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single performance test against an endpoint."""
        try:
            start_time = time.time()
            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "http_time": (end_time - start_time) * 1000,  # ms
                    "lambda_time": data.get("performance_metrics", {}).get("execution_time_ms", 0),
                    "memory_used": data.get("performance_metrics", {}).get("memory_used_mb", 0),
                    "cold_start": data.get("cold_start", False),
                    "architecture": data.get("architecture", "unknown"),
                    "response": data
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def run_comparison_test(self, operation: str, params: Dict[str, Any], iterations: int = 3) -> Dict[str, Any]:
        """Run comparison test between ARM64 and x86_64."""
        if self.verbose:
            print(f"\n🧪 Running {operation} comparison test ({iterations} iterations)")
            print("=" * 60)
        
        payload = {"operation": operation, **params}
        
        arm64_results = []
        x86_results = []
        
        # Run tests alternating between architectures to minimize bias
        for i in range(iterations):
            if self.verbose:
                print(f"Iteration {i+1}/{iterations}...")
            
            # Test ARM64
            arm64_result = self.run_single_test(self.arm64_url, payload)
            if arm64_result["success"]:
                arm64_results.append(arm64_result)
                if self.verbose:
                    print(f"  ARM64: {arm64_result['lambda_time']:.2f}ms")
            else:
                if self.verbose:
                    print(f"  ARM64: FAILED - {arm64_result['error']}")
            
            # Small delay between tests
            time.sleep(1)
            
            # Test x86_64
            x86_result = self.run_single_test(self.x86_url, payload)
            if x86_result["success"]:
                x86_results.append(x86_result)
                if self.verbose:
                    print(f"  x86_64: {x86_result['lambda_time']:.2f}ms")
            else:
                if self.verbose:
                    print(f"  x86_64: FAILED - {x86_result['error']}")
            
            # Delay between iterations
            if i < iterations - 1:
                time.sleep(2)
        
        return self.analyze_results(operation, arm64_results, x86_results)
    
    def analyze_results(self, operation: str, arm64_results: List[Dict], x86_results: List[Dict]) -> Dict[str, Any]:
        """Analyze and compare test results."""
        if not arm64_results or not x86_results:
            return {"error": "Insufficient data for comparison"}
        
        # Calculate statistics
        arm64_times = [r["lambda_time"] for r in arm64_results]
        x86_times = [r["lambda_time"] for r in x86_results]
        
        arm64_memory = [r["memory_used"] for r in arm64_results]
        x86_memory = [r["memory_used"] for r in x86_results]
        
        analysis = {
            "operation": operation,
            "test_count": len(arm64_results),
            "arm64": {
                "avg_time_ms": statistics.mean(arm64_times),
                "min_time_ms": min(arm64_times),
                "max_time_ms": max(arm64_times),
                "std_dev_ms": statistics.stdev(arm64_times) if len(arm64_times) > 1 else 0,
                "avg_memory_mb": statistics.mean(arm64_memory),
                "cold_starts": sum(1 for r in arm64_results if r["cold_start"])
            },
            "x86_64": {
                "avg_time_ms": statistics.mean(x86_times),
                "min_time_ms": min(x86_times),
                "max_time_ms": max(x86_times),
                "std_dev_ms": statistics.stdev(x86_times) if len(x86_times) > 1 else 0,
                "avg_memory_mb": statistics.mean(x86_memory),
                "cold_starts": sum(1 for r in x86_results if r["cold_start"])
            }
        }
        
        # Calculate performance comparison
        arm64_avg = analysis["arm64"]["avg_time_ms"]
        x86_avg = analysis["x86_64"]["avg_time_ms"]
        
        if x86_avg > 0:
            performance_ratio = arm64_avg / x86_avg
            if performance_ratio < 1:
                analysis["winner"] = "ARM64"
                analysis["performance_improvement"] = f"{((1 - performance_ratio) * 100):.1f}% faster"
            else:
                analysis["winner"] = "x86_64"
                analysis["performance_improvement"] = f"{((performance_ratio - 1) * 100):.1f}% faster"
        
        return analysis
    
    def print_analysis(self, analysis: Dict[str, Any]):
        """Print formatted analysis results."""
        if "error" in analysis:
            print(f"❌ Analysis failed: {analysis['error']}")
            return
        
        if self.verbose:
            print(f"\n📊 Performance Analysis: {analysis['operation']}")
            print("=" * 60)
            
            # ARM64 Results
            arm64 = analysis["arm64"]
            print(f"🔵 ARM64 (Graviton2):")
            print(f"   Average: {arm64['avg_time_ms']:.2f}ms")
            print(f"   Range: {arm64['min_time_ms']:.2f}ms - {arm64['max_time_ms']:.2f}ms")
            print(f"   Std Dev: {arm64['std_dev_ms']:.2f}ms")
            print(f"   Memory: {arm64['avg_memory_mb']:.1f}MB")
            print(f"   Cold Starts: {arm64['cold_starts']}")
            
            # x86_64 Results
            x86 = analysis["x86_64"]
            print(f"\n🔴 x86_64:")
            print(f"   Average: {x86['avg_time_ms']:.2f}ms")
            print(f"   Range: {x86['min_time_ms']:.2f}ms - {x86['max_time_ms']:.2f}ms")
            print(f"   Std Dev: {x86['std_dev_ms']:.2f}ms")
            print(f"   Memory: {x86['avg_memory_mb']:.1f}MB")
            print(f"   Cold Starts: {x86['cold_starts']}")
            
            # Winner
            if "winner" in analysis:
                winner_emoji = "🔵" if analysis["winner"] == "ARM64" else "🔴"
                print(f"\n🏆 Winner: {winner_emoji} {analysis['winner']} ({analysis['performance_improvement']})")
    
    def run_comprehensive_test(self, iterations: int = 3, output_file: str = None) -> List[Dict[str, Any]]:
        """Run comprehensive performance comparison across all operations."""
        if self.verbose:
            print("🚀 Lambda Performance Comparison - Comprehensive Test")
            print("=" * 60)
            print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        test_cases = [
            {
                "operation": "sort_intensive",
                "params": {"data_size": 8000, "iterations": 1},
                "iterations": iterations
            },
            {
                "operation": "mathematical_computation", 
                "params": {"complexity": 2000, "iterations": 1},
                "iterations": iterations
            },
            {
                "operation": "string_processing",
                "params": {"text_size": 15000, "iterations": 1},
                "iterations": iterations
            },
            {
                "operation": "memory_intensive",
                "params": {"memory_size_mb": 20, "iterations": 1},
                "iterations": iterations
            }
        ]
        
        results = []
        
        for test_case in test_cases:
            analysis = self.run_comparison_test(
                test_case["operation"],
                test_case["params"],
                test_case["iterations"]
            )
            
            if "error" not in analysis:
                results.append(analysis)
                self.print_analysis(analysis)
            else:
                if self.verbose:
                    print(f"❌ Test failed: {analysis['error']}")
        
        # Overall summary
        if results and self.verbose:
            self.print_overall_summary(results)
        
        # Save results if output file specified
        if output_file and results:
            self.save_results(results, output_file)
        
        if self.verbose:
            print(f"\n✅ Testing completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return results
    
    def print_overall_summary(self, results: List[Dict[str, Any]]):
        """Print overall performance summary."""
        print(f"\n🎯 Overall Performance Summary")
        print("=" * 60)
        
        arm64_wins = 0
        x86_wins = 0
        
        for result in results:
            if "winner" in result:
                if result["winner"] == "ARM64":
                    arm64_wins += 1
                else:
                    x86_wins += 1
                
                print(f"{result['operation']:25} → {result['winner']} ({result['performance_improvement']})")
        
        print(f"\n📈 Score: ARM64: {arm64_wins} | x86_64: {x86_wins}")
        
        if arm64_wins > x86_wins:
            print("🏆 Overall Winner: ARM64 (Graviton2)")
        elif x86_wins > arm64_wins:
            print("🏆 Overall Winner: x86_64")
        else:
            print("🤝 Overall Result: Tie")
    
    def save_results(self, results: List[Dict[str, Any]], filename: str):
        """Save results to JSON file."""
        output_data = {
            "test_timestamp": datetime.now().isoformat(),
            "test_configuration": {
                "arm64_url": self.arm64_url,
                "x86_url": self.x86_url
            },
            "results": results
        }
        
        with open(filename, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        if self.verbose:
            print(f"\n💾 Results saved to: {filename}")


def get_sam_stack_outputs(stack_name: str = "lambda-performance-comparison", region: str = None) -> Dict[str, str]:
    """Fetch stack outputs from AWS CloudFormation to get endpoint URLs."""
    try:
        # Build AWS CLI command
        cmd = ["aws", "cloudformation", "describe-stacks", "--stack-name", stack_name]
        if region:
            cmd.extend(["--region", region])
        cmd.extend(["--query", "Stacks[0].Outputs", "--output", "json"])
        
        # Execute command
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        outputs = json.loads(result.stdout)
        
        # Extract URLs
        urls = {}
        for output in outputs:
            key = output.get("OutputKey", "")
            value = output.get("OutputValue", "")
            
            if key == "Arm64EndpointUrl":
                urls["arm64_url"] = value
            elif key == "X86EndpointUrl":
                urls["x86_url"] = value
        
        return urls
        
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to get stack outputs: {e.stderr}")
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse stack outputs: {e}")
    except Exception as e:
        raise Exception(f"Error fetching stack outputs: {e}")


def get_sam_config() -> Dict[str, str]:
    """Read SAM configuration to get stack name and region."""
    config = {"stack_name": "lambda-performance-comparison", "region": None}
    
    try:
        # Try to read samconfig.toml
        if os.path.exists("samconfig.toml"):
            with open("samconfig.toml", "r") as f:
                content = f.read()
                
                # Simple parsing for stack_name and region
                for line in content.split("\n"):
                    line = line.strip()
                    if line.startswith("stack_name"):
                        config["stack_name"] = line.split("=")[1].strip().strip('"')
                    elif line.startswith("region") and "region" not in config:
                        config["region"] = line.split("=")[1].strip().strip('"')
    except Exception:
        # Use defaults if config reading fails
        pass
    
    return config


def main():
    """Main function with command line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Lambda Performance Comparison Testing",
        epilog="""
Examples:
  # Run with auto-detected URLs from SAM stack
  python performance_test.py
  
  # Run specific operation only
  python performance_test.py --operation mathematical_computation
  
  # Run with custom URLs
  python performance_test.py --arm64-url https://... --x86-url https://...
  
  # Save results to file
  python performance_test.py --output results.json
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--arm64-url", help="ARM64 Lambda endpoint URL (auto-detected from SAM stack if not provided)")
    parser.add_argument("--x86-url", help="x86_64 Lambda endpoint URL (auto-detected from SAM stack if not provided)")
    parser.add_argument("--stack-name", help="CloudFormation stack name (default: from samconfig.toml)")
    parser.add_argument("--region", help="AWS region (default: from samconfig.toml)")
    parser.add_argument("--iterations", type=int, default=3, help="Number of test iterations")
    parser.add_argument("--output", help="Output file for results (JSON format)")
    parser.add_argument("--quiet", action="store_true", help="Suppress verbose output")
    parser.add_argument("--operation", help="Run specific operation only", 
                       choices=["sort_intensive", "mathematical_computation", "string_processing", "memory_intensive"])
    
    args = parser.parse_args()
    
    # Get URLs from command line or auto-detect from SAM stack
    arm64_url = args.arm64_url
    x86_url = args.x86_url
    
    if not arm64_url or not x86_url:
        if not args.quiet:
            print("🔍 Auto-detecting endpoint URLs from SAM stack...")
        
        try:
            # Get SAM configuration
            sam_config = get_sam_config()
            stack_name = args.stack_name or sam_config["stack_name"]
            region = args.region or sam_config["region"]
            
            # Fetch URLs from stack outputs
            urls = get_sam_stack_outputs(stack_name, region)
            
            if not arm64_url:
                arm64_url = urls.get("arm64_url")
            if not x86_url:
                x86_url = urls.get("x86_url")
            
            if not arm64_url or not x86_url:
                print("❌ Could not find both endpoint URLs in stack outputs")
                print("Available outputs:", list(urls.keys()))
                sys.exit(1)
            
            if not args.quiet:
                print(f"✅ Found ARM64 URL: {arm64_url}")
                print(f"✅ Found x86_64 URL: {x86_url}")
                
        except Exception as e:
            print(f"❌ Failed to auto-detect URLs: {e}")
            print("Please provide --arm64-url and --x86-url manually")
            sys.exit(1)
    
    tester = PerformanceTester(arm64_url, x86_url, verbose=not args.quiet)
    
    if args.operation:
        # Run single operation
        test_params = {
            "sort_intensive": {"data_size": 8000, "iterations": 1},
            "mathematical_computation": {"complexity": 2000, "iterations": 1},
            "string_processing": {"text_size": 15000, "iterations": 1},
            "memory_intensive": {"memory_size_mb": 20, "iterations": 1}
        }
        
        result = tester.run_comparison_test(args.operation, test_params[args.operation], args.iterations)
        tester.print_analysis(result)
        
        if args.output:
            tester.save_results([result], args.output)
    else:
        # Run comprehensive test
        results = tester.run_comprehensive_test(args.iterations, args.output)
        
        if not results:
            print("❌ No successful test results")
            sys.exit(1)


if __name__ == "__main__":
    main()