#!/usr/bin/env python3
"""
Local testing script for Lambda Performance Comparison.

This script demonstrates how to test Lambda functions locally using SAM CLI
and provides utilities for running various test scenarios.
"""

import json
import subprocess
import sys
import time
import os
from typing import Dict, List, Any
import requests
import threading
from concurrent.futures import ThreadPoolExecutor


class LocalTester:
    """Local testing utilities for Lambda functions."""
    
    def __init__(self):
        self.api_port = 3000
        self.api_url = f"http://localhost:{self.api_port}"
        self.events_dir = "events"
        
    def test_direct_invocation(self, function_name: str, event_file: str) -> Dict[str, Any]:
        """
        Test Lambda function with direct invocation using SAM CLI.
        
        Args:
            function_name: Name of the Lambda function (ProcessorFunctionArm64 or ProcessorFunctionX86)
            event_file: Path to the event JSON file
            
        Returns:
            Test result dictionary
        """
        print(f"\n🧪 Testing {function_name} with {event_file}")
        
        cmd = [
            "sam", "local", "invoke",
            function_name,
            "--event", event_file,
            "--env-vars", "env.json"
        ]
        
        try:
            start_time = time.time()
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            end_time = time.time()
            
            if result.returncode == 0:
                try:
                    response_data = json.loads(result.stdout)
                    return {
                        "success": True,
                        "function": function_name,
                        "event_file": event_file,
                        "execution_time": end_time - start_time,
                        "response": response_data,
                        "stdout": result.stdout,
                        "stderr": result.stderr
                    }
                except json.JSONDecodeError:
                    return {
                        "success": False,
                        "function": function_name,
                        "event_file": event_file,
                        "error": "Invalid JSON response",
                        "stdout": result.stdout,
                        "stderr": result.stderr
                    }
            else:
                return {
                    "success": False,
                    "function": function_name,
                    "event_file": event_file,
                    "error": f"Command failed with return code {result.returncode}",
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "function": function_name,
                "event_file": event_file,
                "error": "Test timed out after 60 seconds"
            }
        except Exception as e:
            return {
                "success": False,
                "function": function_name,
                "event_file": event_file,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def test_api_gateway_local(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test API Gateway endpoint running locally.
        
        Args:
            endpoint: API endpoint path (e.g., "/process-arm64")
            payload: Request payload
            
        Returns:
            Test result dictionary
        """
        url = f"{self.api_url}{endpoint}"
        print(f"\n🌐 Testing API Gateway: POST {url}")
        
        try:
            start_time = time.time()
            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            end_time = time.time()
            
            return {
                "success": response.status_code == 200,
                "endpoint": endpoint,
                "payload": payload,
                "status_code": response.status_code,
                "execution_time": end_time - start_time,
                "response": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                "headers": dict(response.headers)
            }
            
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "endpoint": endpoint,
                "error": "Connection failed. Make sure 'sam local start-api' is running."
            }
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "endpoint": endpoint,
                "error": "Request timed out after 30 seconds"
            }
        except Exception as e:
            return {
                "success": False,
                "endpoint": endpoint,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def run_direct_invocation_tests(self) -> List[Dict[str, Any]]:
        """
        Run all direct invocation tests.
        
        Returns:
            List of test results
        """
        print("🚀 Running Direct Invocation Tests")
        print("=" * 50)
        
        test_cases = [
            ("ProcessorFunctionArm64", "events/direct-invocation-sort.json"),
            ("ProcessorFunctionX86", "events/direct-invocation-sort.json"),
            ("ProcessorFunctionArm64", "events/direct-invocation-math.json"),
            ("ProcessorFunctionX86", "events/direct-invocation-math.json"),
            ("ProcessorFunctionArm64", "events/direct-invocation-string.json"),
            ("ProcessorFunctionX86", "events/direct-invocation-string.json"),
            ("ProcessorFunctionArm64", "events/direct-invocation-memory.json"),
            ("ProcessorFunctionX86", "events/direct-invocation-memory.json"),
        ]
        
        results = []
        for function_name, event_file in test_cases:
            result = self.test_direct_invocation(function_name, event_file)
            results.append(result)
            
            if result["success"]:
                print(f"✅ {function_name} with {event_file}: SUCCESS")
                if "response" in result and "body" in result["response"]:
                    body = json.loads(result["response"]["body"])
                    if "performance_metrics" in body:
                        metrics = body["performance_metrics"]
                        print(f"   ⏱️  Execution time: {metrics.get('execution_time_ms', 'N/A')} ms")
                        print(f"   💾 Memory used: {metrics.get('memory_used_mb', 'N/A')} MB")
            else:
                print(f"❌ {function_name} with {event_file}: FAILED")
                print(f"   Error: {result.get('error', 'Unknown error')}")
        
        return results
    
    def run_api_gateway_tests(self) -> List[Dict[str, Any]]:
        """
        Run API Gateway tests.
        
        Returns:
            List of test results
        """
        print("\n🌐 Running API Gateway Tests")
        print("=" * 50)
        
        test_cases = [
            ("/process-arm64", {"operation": "sort_intensive", "data_size": 5000, "iterations": 1}),
            ("/process-x86", {"operation": "sort_intensive", "data_size": 5000, "iterations": 1}),
            ("/process-arm64", {"operation": "mathematical_computation", "complexity": 2000, "iterations": 1}),
            ("/process-x86", {"operation": "mathematical_computation", "complexity": 2000, "iterations": 1}),
            ("/process-arm64", {"operation": "string_processing", "text_size": 10000, "iterations": 1}),
            ("/process-x86", {"operation": "string_processing", "text_size": 10000, "iterations": 1}),
        ]
        
        results = []
        for endpoint, payload in test_cases:
            result = self.test_api_gateway_local(endpoint, payload)
            results.append(result)
            
            if result["success"]:
                print(f"✅ {endpoint}: SUCCESS")
                if "response" in result and "performance_metrics" in result["response"]:
                    metrics = result["response"]["performance_metrics"]
                    print(f"   ⏱️  Execution time: {metrics.get('execution_time_ms', 'N/A')} ms")
                    print(f"   💾 Memory used: {metrics.get('memory_used_mb', 'N/A')} MB")
            else:
                print(f"❌ {endpoint}: FAILED")
                print(f"   Error: {result.get('error', 'Unknown error')}")
        
        return results
    
    def create_env_file(self):
        """Create environment variables file for local testing."""
        env_vars = {
            "ProcessorFunctionArm64": {
                "ARCHITECTURE": "arm64",
                "PYTHONPATH": "/var/task/src"
            },
            "ProcessorFunctionX86": {
                "ARCHITECTURE": "x86_64", 
                "PYTHONPATH": "/var/task/src"
            }
        }
        
        with open("env.json", "w") as f:
            json.dump(env_vars, f, indent=2)
        
        print("📝 Created env.json file for local testing")
    
    def print_usage_instructions(self):
        """Print usage instructions for local testing."""
        print("\n📋 Local Testing Instructions")
        print("=" * 50)
        print("1. Build the SAM application:")
        print("   sam build")
        print()
        print("2. For Direct Invocation Testing:")
        print("   python local_test.py --direct")
        print("   # Or manually:")
        print("   sam local invoke ProcessorFunctionArm64 --event events/direct-invocation-sort.json")
        print()
        print("3. For API Gateway Testing:")
        print("   # Start local API Gateway (in separate terminal):")
        print("   sam local start-api --port 3000")
        print("   # Then run tests:")
        print("   python local_test.py --api")
        print()
        print("4. For Interactive Testing:")
        print("   # Start local API and test with curl:")
        print("   curl -X POST http://localhost:3000/process-arm64 \\")
        print("        -H 'Content-Type: application/json' \\")
        print("        -d '{\"operation\": \"sort_intensive\", \"data_size\": 5000}'")
        print()
        print("5. Available Event Files:")
        for file in os.listdir("events"):
            if file.endswith(".json"):
                print(f"   - events/{file}")


def main():
    """Main function for running local tests."""
    tester = LocalTester()
    
    # Create environment file
    tester.create_env_file()
    
    if len(sys.argv) > 1:
        if "--direct" in sys.argv:
            results = tester.run_direct_invocation_tests()
            print(f"\n📊 Direct Invocation Tests: {sum(1 for r in results if r['success'])}/{len(results)} passed")
            
        elif "--api" in sys.argv:
            results = tester.run_api_gateway_tests()
            print(f"\n📊 API Gateway Tests: {sum(1 for r in results if r['success'])}/{len(results)} passed")
            
        elif "--help" in sys.argv:
            tester.print_usage_instructions()
        else:
            print("Usage: python local_test.py [--direct|--api|--help]")
    else:
        tester.print_usage_instructions()


if __name__ == "__main__":
    main()