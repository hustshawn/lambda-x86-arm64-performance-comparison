#!/usr/bin/env python3
"""
Manual test script for the Lambda function handler.
"""

import sys
import os
import json
from unittest.mock import Mock

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from lambda_function import lambda_handler

def test_direct_invocation():
    """Test direct Lambda invocation."""
    print("Testing direct invocation...")
    
    # Mock context
    context = Mock()
    context.function_name = 'test-function'
    context.function_version = '1'
    
    # Test event
    event = {
        'operation': 'sort_intensive',
        'data_size': 1000,
        'iterations': 1
    }
    
    # Set environment variable for architecture
    os.environ['ARCHITECTURE'] = 'x86_64'
    
    try:
        response = lambda_handler(event, context)
        print(f"Status Code: {response['statusCode']}")
        
        if response['statusCode'] == 200:
            body = json.loads(response['body'])
            print(f"Success: {body['success']}")
            print(f"Operation: {body['operation']}")
            print(f"Architecture: {body['architecture']}")
            print(f"Cold Start: {body['cold_start']}")
            print("✅ Direct invocation test passed!")
        else:
            body = json.loads(response['body'])
            print(f"Error: {body['error']}")
            print("❌ Direct invocation test failed!")
            
    except Exception as e:
        print(f"Exception: {e}")
        print("❌ Direct invocation test failed!")

def test_api_gateway_invocation():
    """Test API Gateway invocation."""
    print("\nTesting API Gateway invocation...")
    
    # Mock context
    context = Mock()
    context.function_name = 'test-function'
    context.function_version = '1'
    
    # Test API Gateway event
    event = {
        'httpMethod': 'POST',
        'body': json.dumps({
            'operation': 'mathematical_computation',
            'complexity': 500,
            'iterations': 1
        }),
        'queryStringParameters': None
    }
    
    try:
        response = lambda_handler(event, context)
        print(f"Status Code: {response['statusCode']}")
        
        if response['statusCode'] == 200:
            body = json.loads(response['body'])
            print(f"Success: {body['success']}")
            print(f"Operation: {body['operation']}")
            print(f"Architecture: {body['architecture']}")
            print("✅ API Gateway invocation test passed!")
        else:
            body = json.loads(response['body'])
            print(f"Error: {body['error']}")
            print("❌ API Gateway invocation test failed!")
            
    except Exception as e:
        print(f"Exception: {e}")
        print("❌ API Gateway invocation test failed!")

def test_error_handling():
    """Test error handling."""
    print("\nTesting error handling...")
    
    # Mock context
    context = Mock()
    context.function_name = 'test-function'
    context.function_version = '1'
    
    # Test event with missing operation
    event = {
        'data_size': 1000
    }
    
    try:
        response = lambda_handler(event, context)
        print(f"Status Code: {response['statusCode']}")
        
        if response['statusCode'] == 400:
            body = json.loads(response['body'])
            print(f"Error: {body['error']}")
            print("✅ Error handling test passed!")
        else:
            print("❌ Error handling test failed!")
            
    except Exception as e:
        print(f"Exception: {e}")
        print("❌ Error handling test failed!")

if __name__ == '__main__':
    test_direct_invocation()
    test_api_gateway_invocation()
    test_error_handling()