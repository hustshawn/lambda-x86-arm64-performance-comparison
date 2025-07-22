#!/usr/bin/env python3
"""
Validation script for local testing setup.

This script validates that all components for local testing are properly configured.
"""

import json
import os
import sys
from pathlib import Path


def validate_files():
    """Validate that all required files exist and are properly formatted."""
    print("🔍 Validating local testing setup...")
    
    required_files = [
        "template.yaml",
        "samconfig.toml", 
        "env.json",
        "local_test.py",
        "LOCAL_TESTING.md"
    ]
    
    event_files = [
        "events/direct-invocation-sort.json",
        "events/direct-invocation-math.json", 
        "events/direct-invocation-string.json",
        "events/direct-invocation-memory.json",
        "events/api-gateway-sort.json",
        "events/api-gateway-math.json"
    ]
    
    all_files = required_files + event_files
    missing_files = []
    
    for file_path in all_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print(f"\n❌ Missing files: {missing_files}")
        return False
    
    return True


def validate_json_files():
    """Validate JSON file formats."""
    print("\n🔍 Validating JSON files...")
    
    json_files = [
        "env.json",
        "events/direct-invocation-sort.json",
        "events/direct-invocation-math.json",
        "events/direct-invocation-string.json", 
        "events/direct-invocation-memory.json",
        "events/api-gateway-sort.json",
        "events/api-gateway-math.json"
    ]
    
    for file_path in json_files:
        try:
            with open(file_path, 'r') as f:
                json.load(f)
            print(f"✅ {file_path} - Valid JSON")
        except json.JSONDecodeError as e:
            print(f"❌ {file_path} - Invalid JSON: {e}")
            return False
        except FileNotFoundError:
            print(f"❌ {file_path} - File not found")
            return False
    
    return True


def validate_event_schemas():
    """Validate event file schemas."""
    print("\n🔍 Validating event schemas...")
    
    # Validate direct invocation events
    direct_events = [
        "events/direct-invocation-sort.json",
        "events/direct-invocation-math.json",
        "events/direct-invocation-string.json",
        "events/direct-invocation-memory.json"
    ]
    
    for event_file in direct_events:
        with open(event_file, 'r') as f:
            event = json.load(f)
        
        if 'operation' not in event:
            print(f"❌ {event_file} - Missing 'operation' field")
            return False
        
        valid_operations = ['sort_intensive', 'mathematical_computation', 'string_processing', 'memory_intensive']
        if event['operation'] not in valid_operations:
            print(f"❌ {event_file} - Invalid operation: {event['operation']}")
            return False
        
        print(f"✅ {event_file} - Valid schema")
    
    # Validate API Gateway events
    api_events = [
        "events/api-gateway-sort.json",
        "events/api-gateway-math.json"
    ]
    
    for event_file in api_events:
        with open(event_file, 'r') as f:
            event = json.load(f)
        
        required_fields = ['httpMethod', 'body', 'headers']
        for field in required_fields:
            if field not in event:
                print(f"❌ {event_file} - Missing '{field}' field")
                return False
        
        # Validate body is valid JSON
        try:
            body = json.loads(event['body'])
            if 'operation' not in body:
                print(f"❌ {event_file} - Body missing 'operation' field")
                return False
        except json.JSONDecodeError:
            print(f"❌ {event_file} - Invalid JSON in body")
            return False
        
        print(f"✅ {event_file} - Valid schema")
    
    return True


def validate_environment_config():
    """Validate environment configuration."""
    print("\n🔍 Validating environment configuration...")
    
    with open('env.json', 'r') as f:
        env_config = json.load(f)
    
    required_functions = ['ProcessorFunctionArm64', 'ProcessorFunctionX86']
    
    for func_name in required_functions:
        if func_name not in env_config:
            print(f"❌ Missing function config: {func_name}")
            return False
        
        func_config = env_config[func_name]
        if 'ARCHITECTURE' not in func_config:
            print(f"❌ {func_name} missing ARCHITECTURE env var")
            return False
        
        if 'PYTHONPATH' not in func_config:
            print(f"❌ {func_name} missing PYTHONPATH env var")
            return False
        
        print(f"✅ {func_name} - Valid configuration")
    
    return True


def print_usage_summary():
    """Print usage summary."""
    print("\n📋 Local Testing Usage Summary")
    print("=" * 50)
    print("1. Build: sam build")
    print("2. Direct tests: python local_test.py --direct")
    print("3. API tests: sam local start-api --port 3000 & python local_test.py --api")
    print("4. Manual invoke: sam local invoke ProcessorFunctionArm64 --event events/direct-invocation-sort.json")
    print("5. Manual API test: curl -X POST http://localhost:3000/process-arm64 -H 'Content-Type: application/json' -d '{\"operation\": \"sort_intensive\", \"data_size\": 5000}'")


def main():
    """Main validation function."""
    print("🧪 Lambda Performance Comparison - Local Testing Validation")
    print("=" * 60)
    
    validations = [
        ("File existence", validate_files),
        ("JSON format", validate_json_files), 
        ("Event schemas", validate_event_schemas),
        ("Environment config", validate_environment_config)
    ]
    
    all_passed = True
    
    for name, validation_func in validations:
        if not validation_func():
            print(f"\n❌ {name} validation failed")
            all_passed = False
        else:
            print(f"\n✅ {name} validation passed")
    
    if all_passed:
        print("\n🎉 All validations passed! Local testing setup is ready.")
        print_usage_summary()
        return 0
    else:
        print("\n💥 Some validations failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())