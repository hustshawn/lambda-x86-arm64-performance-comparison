#!/usr/bin/env python3
"""
Example performance test script for Lambda Performance Comparison.

This script demonstrates how to run custom performance tests and analyze results.
Modify the test parameters and add your own test scenarios as needed.
"""

import requests
import json
import time
import statistics
from typing import Dict, List, Any
from datetime import datetime


class CustomPerformanceTester:
    """Custom performance testing example."""
    
    def __init__(self, arm64_url: str, x86_url: str):
        """
        Initialize with your deployed endpoint URLs.
        
        Args:
            arm64_url: ARM64 Lambda endpoint URL
            x86_url: x86_64 Lambda endpoint URL
        """
        self.arm64_url = arm64_url
        self.x86_url = x86_url
        
    def run_custom_test(self, test_name: str, operation: str, params: Dict[str, Any], iterations: int = 5):
        """Run a custom performance test."""
        print(f"\n🧪 Running {test_name}")
        print("=" * 60)
        
        payload = {"operation": operation, **params}
        
        arm64_times = []
        x86_times = []
        
        for i in range(iterations):
            print(f"Iteration {i+1}/{iterations}...")
            
            # Test ARM64
            start_time = time.time()
            arm64_response = requests.post(self.arm64_url, json=payload, timeout=60)
            arm64_http_time = (time.time() - start_time) * 1000
            
            if arm64_response.status_code == 200:
                arm64_data = arm64_response.json()
                arm64_lambda_time = arm64_data.get("performance_metrics", {}).get("execution_time_ms", 0)
                arm64_times.append(arm64_lambda_time)
                print(f"  ARM64: {arm64_lambda_time:.2f}ms (HTTP: {arm64_http_time:.2f}ms)")
            else:
                print(f"  ARM64: FAILED - {arm64_response.status_code}")
            
            time.sleep(1)  # Brief pause between tests
            
            # Test x86_64
            start_time = time.time()
            x86_response = requests.post(self.x86_url, json=payload, timeout=60)
            x86_http_time = (time.time() - start_time) * 1000
            
            if x86_response.status_code == 200:
                x86_data = x86_response.json()
                x86_lambda_time = x86_data.get("performance_metrics", {}).get("execution_time_ms", 0)
                x86_times.append(x86_lambda_time)
                print(f"  x86_64: {x86_lambda_time:.2f}ms (HTTP: {x86_http_time:.2f}ms)")
            else:
                print(f"  x86_64: FAILED - {x86_response.status_code}")
            
            if i < iterations - 1:
                time.sleep(2)  # Pause between iterations
        
        # Analyze results
        if arm64_times and x86_times:
            self.analyze_custom_results(test_name, arm64_times, x86_times)
        else:
            print("❌ Insufficient data for analysis")
    
    def analyze_custom_results(self, test_name: str, arm64_times: List[float], x86_times: List[float]):
        """Analyze and display custom test results."""
        arm64_avg = statistics.mean(arm64_times)
        x86_avg = statistics.mean(x86_times)
        
        improvement = ((x86_avg - arm64_avg) / x86_avg) * 100
        
        print(f"\n📊 Results for {test_name}:")
        print(f"ARM64 Average: {arm64_avg:.2f}ms")
        print(f"x86_64 Average: {x86_avg:.2f}ms")
        
        if improvement > 0:
            print(f"🏆 ARM64 is {improvement:.1f}% faster")
        else:
            print(f"🏆 x86_64 is {abs(improvement):.1f}% faster")
        
        # Statistical analysis
        if len(arm64_times) > 1:
            arm64_std = statistics.stdev(arm64_times)
            x86_std = statistics.stdev(x86_times)
            print(f"ARM64 Std Dev: {arm64_std:.2f}ms")
            print(f"x86_64 Std Dev: {x86_std:.2f}ms")


def main():
    """Example usage of custom performance testing."""
    
    # Replace these URLs with your deployed endpoints
    ARM64_URL = "https://your-api-gateway-url/process-arm64"
    X86_URL = "https://your-api-gateway-url/process-x86"
    
    print("🚀 Custom Performance Testing Example")
    print("=" * 60)
    print("This script demonstrates custom performance testing scenarios.")
    print("Modify the test cases below for your specific needs.")
    print()
    
    # Check if URLs are configured
    if "your-api-gateway-url" in ARM64_URL:
        print("❌ Please update the ARM64_URL and X86_URL variables with your deployed endpoints")
        print("   You can find these URLs in the SAM deployment output or DEPLOYMENT_GUIDE.md")
        return
    
    tester = CustomPerformanceTester(ARM64_URL, X86_URL)
    
    # Example Test 1: Small data sorting
    tester.run_custom_test(
        test_name="Small Data Sorting",
        operation="sort_intensive",
        params={"data_size": 1000, "iterations": 1},
        iterations=3
    )
    
    # Example Test 2: Large data sorting
    tester.run_custom_test(
        test_name="Large Data Sorting",
        operation="sort_intensive", 
        params={"data_size": 50000, "iterations": 1},
        iterations=3
    )
    
    # Example Test 3: Light mathematical computation
    tester.run_custom_test(
        test_name="Light Math Computation",
        operation="mathematical_computation",
        params={"complexity": 500, "iterations": 1},
        iterations=3
    )
    
    # Example Test 4: Heavy mathematical computation
    tester.run_custom_test(
        test_name="Heavy Math Computation",
        operation="mathematical_computation",
        params={"complexity": 5000, "iterations": 1},
        iterations=3
    )
    
    # Example Test 5: String processing variations
    tester.run_custom_test(
        test_name="Small Text Processing",
        operation="string_processing",
        params={"text_size": 5000, "iterations": 1},
        iterations=3
    )
    
    tester.run_custom_test(
        test_name="Large Text Processing",
        operation="string_processing",
        params={"text_size": 50000, "iterations": 1},
        iterations=3
    )
    
    # Example Test 6: Memory operations
    tester.run_custom_test(
        test_name="Small Memory Operations",
        operation="memory_intensive",
        params={"memory_size_mb": 5, "iterations": 1},
        iterations=3
    )
    
    tester.run_custom_test(
        test_name="Large Memory Operations",
        operation="memory_intensive",
        params={"memory_size_mb": 50, "iterations": 1},
        iterations=3
    )
    
    print("\n✅ Custom performance testing completed!")
    print("\n💡 Tips for custom testing:")
    print("- Modify test parameters to match your use case")
    print("- Add more iterations for better statistical significance")
    print("- Test with different data sizes to find performance curves")
    print("- Monitor CloudWatch metrics for additional insights")
    print("- Consider testing at different times of day")


if __name__ == "__main__":
    main()