#!/usr/bin/env python3
"""
Performance testing script for deployed Lambda Performance Comparison solution.

This script runs performance tests against the deployed AWS Lambda functions
and provides comparative analysis between ARM64 and x86_64 architectures.
"""

import requests
import json
import time
import statistics
from typing import Dict, List, Any
from datetime import datetime


class PerformanceTester:
    """Performance testing utility for deployed Lambda functions."""
    
    def __init__(self):
        # Update these URLs with your deployed endpoints
        self.arm64_url = "https://e397dnqfv5.execute-api.us-west-2.amazonaws.com/dev/process-arm64"
        self.x86_url = "https://e397dnqfv5.execute-api.us-west-2.amazonaws.com/dev/process-x86"
        
    def run_single_test(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single performance test."""
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
        print(f"\n🧪 Running {operation} comparison test ({iterations} iterations)")
        print("=" * 60)
        
        payload = {"operation": operation, **params}
        
        arm64_results = []
        x86_results = []
        
        # Run tests alternating between architectures to minimize bias
        for i in range(iterations):
            print(f"Iteration {i+1}/{iterations}...")
            
            # Test ARM64
            arm64_result = self.run_single_test(self.arm64_url, payload)
            if arm64_result["success"]:
                arm64_results.append(arm64_result)
                print(f"  ARM64: {arm64_result['lambda_time']:.2f}ms")
            else:
                print(f"  ARM64: FAILED - {arm64_result['error']}")
            
            # Small delay between tests
            time.sleep(1)
            
            # Test x86_64
            x86_result = self.run_single_test(self.x86_url, payload)
            if x86_result["success"]:
                x86_results.append(x86_result)
                print(f"  x86_64: {x86_result['lambda_time']:.2f}ms")
            else:
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
    
    def run_comprehensive_test(self):
        """Run comprehensive performance comparison across all operations."""
        print("🚀 Lambda Performance Comparison - Comprehensive Test")
        print("=" * 60)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        test_cases = [
            {
                "operation": "sort_intensive",
                "params": {"data_size": 8000, "iterations": 1},
                "iterations": 3
            },
            {
                "operation": "mathematical_computation", 
                "params": {"complexity": 2000, "iterations": 1},
                "iterations": 3
            },
            {
                "operation": "string_processing",
                "params": {"text_size": 15000, "iterations": 1},
                "iterations": 3
            },
            {
                "operation": "memory_intensive",
                "params": {"memory_size_mb": 20, "iterations": 1},
                "iterations": 3
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
                print(f"❌ Test failed: {analysis['error']}")
        
        # Overall summary
        if results:
            self.print_overall_summary(results)
        
        print(f"\n✅ Testing completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
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


def main():
    """Main function to run performance tests."""
    tester = PerformanceTester()
    
    print("Lambda Performance Comparison - Cloud Testing")
    print("This will test your deployed Lambda functions")
    print(f"ARM64 URL: {tester.arm64_url}")
    print(f"x86_64 URL: {tester.x86_url}")
    
    # Run comprehensive test
    tester.run_comprehensive_test()


if __name__ == "__main__":
    main()