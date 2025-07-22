#!/usr/bin/env python3
"""
Local testing utilities for Lambda Performance Comparison.

This script provides comprehensive local testing capabilities using SAM CLI
for development and validation workflows.
"""

import json
import subprocess
import sys
import time
import os
from typing import Dict, List, Any
import requests
import argparse
from pathlib import Path


class LocalTester:
    """Local testing utilities for Lambda functions using SAM CLI."""
    
    def __init__(self, project_root: str = None, verbose: bool = True):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.verbose = verbose
        self.api_port = 3000
        self.api_url = f"http://localhost:{self.api_port}"
        self.events_dir = self.project_root / "events"
        
    def validate_environment(self) -> bool:
        """Validate that required tools and files are available."""
        required_files = [
            "template.yaml",
            "samconfig.toml",
            "config/env.json"
        ]
        
        missing_files = []
        for file in required_files:
            if not (self.project_root / file).exists():
                missing_files.append(file)
        
        if missing_files:
            print(f"❌ Missing required files: {missing_files}")
            return False
        
        # Check SAM CLI
        try:
            result = subprocess.run(["sam", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ SAM CLI not found or not working")
                return False
        except FileNotFoundError:
            print("❌ SAM CLI not installed")
            return False
        
        return True
    
    def test_direct_invocation(self, function_name: str, event_file: str) -> Dict[str, Any]:
        """Test Lambda function with direct invocation using SAM CLI."""
        if self.verbose:
            print(f"\n🧪 Testing {function_name} with {event_file}")
        
        event_path = self.events_dir / event_file
        if not event_path.exists():
            return {
                "success": False,
                "error": f"Event file not found: {event_path}"
            }
        
        cmd = [
            "sam", "local", "invoke",
            function_name,
            "--event", str(event_path),
            "--env-vars", str(self.project_root / "config" / "env.json")
        ]
        
        try:
            start_time = time.time()
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=self.project_root
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
        """Test API Gateway endpoint running locally."""
        url = f"{self.api_url}{endpoint}"
        if self.verbose:
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
        """Run all direct invocation tests."""
        if self.verbose:
            print("🚀 Running Direct Invocation Tests")
            print("=" * 50)
        
        test_cases = [
            ("ProcessorFunctionArm64", "direct-invocation-sort.json"),
            ("ProcessorFunctionX86", "direct-invocation-sort.json"),
            ("ProcessorFunctionArm64", "direct-invocation-math.json"),
            ("ProcessorFunctionX86", "direct-invocation-math.json"),
            ("ProcessorFunctionArm64", "direct-invocation-string.json"),
            ("ProcessorFunctionX86", "direct-invocation-string.json"),
            ("ProcessorFunctionArm64", "direct-invocation-memory.json"),
            ("ProcessorFunctionX86", "direct-invocation-memory.json"),
        ]
        
        results = []
        for function_name, event_file in test_cases:
            result = self.test_direct_invocation(function_name, event_file)
            results.append(result)
            
            if result["success"]:
                if self.verbose:
                    print(f"✅ {function_name} with {event_file}: SUCCESS")
                    if "response" in result and "body" in result["response"]:
                        try:
                            body = json.loads(result["response"]["body"])
                            if "performance_metrics" in body:
                                metrics = body["performance_metrics"]
                                print(f"   ⏱️  Execution time: {metrics.get('execution_time_ms', 'N/A')} ms")
                                print(f"   💾 Memory used: {metrics.get('memory_used_mb', 'N/A')} MB")
                        except (json.JSONDecodeError, KeyError):
                            pass
            else:
                if self.verbose:
                    print(f"❌ {function_name} with {event_file}: FAILED")
                    print(f"   Error: {result.get('error', 'Unknown error')}")
        
        return results
    
    def run_api_gateway_tests(self) -> List[Dict[str, Any]]:
        """Run API Gateway tests."""
        if self.verbose:
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
                if self.verbose:
                    print(f"✅ {endpoint}: SUCCESS")
                    if "response" in result and "performance_metrics" in result["response"]:
                        metrics = result["response"]["performance_metrics"]
                        print(f"   ⏱️  Execution time: {metrics.get('execution_time_ms', 'N/A')} ms")
                        print(f"   💾 Memory used: {metrics.get('memory_used_mb', 'N/A')} MB")
            else:
                if self.verbose:
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
        
        config_dir = self.project_root / "config"
        config_dir.mkdir(exist_ok=True)
        env_file = config_dir / "env.json"
        with open(env_file, "w") as f:
            json.dump(env_vars, f, indent=2)
        
        if self.verbose:
            print(f"📝 Created {env_file} for local testing")
    
    def print_usage_instructions(self):
        """Print usage instructions for local testing."""
        print("\n📋 Local Testing Instructions")
        print("=" * 50)
        print("1. Build the SAM application:")
        print("   sam build")
        print()
        print("2. For Direct Invocation Testing:")
        print("   python scripts/local_test.py --direct")
        print("   # Or manually:")
        print("   sam local invoke ProcessorFunctionArm64 --event events/direct-invocation-sort.json")
        print()
        print("3. For API Gateway Testing:")
        print("   # Start local API Gateway (in separate terminal):")
        print("   sam local start-api --port 3000")
        print("   # Then run tests:")
        print("   python scripts/local_test.py --api")
        print()
        print("4. For Interactive Testing:")
        print("   # Start local API and test with curl:")
        print("   curl -X POST http://localhost:3000/process-arm64 \\")
        print("        -H 'Content-Type: application/json' \\")
        print("        -d '{\"operation\": \"sort_intensive\", \"data_size\": 5000}'")
        print()
        print("5. Available Event Files:")
        if self.events_dir.exists():
            for file in self.events_dir.glob("*.json"):
                print(f"   - {file.relative_to(self.project_root)}")


def main():
    """Main function with command line argument parsing."""
    parser = argparse.ArgumentParser(description="Local Lambda Testing Utilities")
    parser.add_argument("--direct", action="store_true", help="Run direct invocation tests")
    parser.add_argument("--api", action="store_true", help="Run API Gateway tests")
    parser.add_argument("--validate", action="store_true", help="Validate local environment")
    parser.add_argument("--create-env", action="store_true", help="Create environment file")
    parser.add_argument("--quiet", action="store_true", help="Suppress verbose output")
    parser.add_argument("--project-root", help="Project root directory", default=".")
    
    args = parser.parse_args()
    
    tester = LocalTester(args.project_root, verbose=not args.quiet)
    
    if args.validate:
        if tester.validate_environment():
            print("✅ Local environment validation passed")
        else:
            print("❌ Local environment validation failed")
            sys.exit(1)
        return
    
    if args.create_env:
        tester.create_env_file()
        return
    
    if not tester.validate_environment():
        print("❌ Environment validation failed. Run with --validate for details.")
        sys.exit(1)
    
    if args.direct:
        results = tester.run_direct_invocation_tests()
        success_count = sum(1 for r in results if r['success'])
        print(f"\n📊 Direct Invocation Tests: {success_count}/{len(results)} passed")
        
    elif args.api:
        results = tester.run_api_gateway_tests()
        success_count = sum(1 for r in results if r['success'])
        print(f"\n📊 API Gateway Tests: {success_count}/{len(results)} passed")
        
    else:
        tester.print_usage_instructions()


if __name__ == "__main__":
    main()