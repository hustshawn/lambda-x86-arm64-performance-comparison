"""
Unit tests for the Lambda function handler.
"""

import unittest
import json
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from lambda_function import (
    lambda_handler, parse_event, parse_api_gateway_event, parse_direct_invocation_event,
    validate_input, validate_operation_parameters, get_default_data_size,
    create_success_response, create_error_response
)


class TestLambdaHandler(unittest.TestCase):
    """Test cases for the main Lambda handler."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Reset global variables
        import lambda_function
        lambda_function._cold_start = True
        lambda_function._metrics_collector = None
        
        # Mock context
        self.mock_context = Mock()
        self.mock_context.function_name = 'test-function'
        self.mock_context.function_version = '1'
    
    @patch('lambda_function.create_metrics_collector')
    @patch('lambda_function.process_workload')
    def test_successful_direct_invocation(self, mock_process_workload, mock_create_metrics):
        """Test successful direct Lambda invocation."""
        # Setup mocks
        mock_metrics = Mock()
        mock_metrics.architecture = 'x86_64'
        mock_metrics.function_name = 'test-function'
        mock_metrics.function_version = '1'
        mock_metrics.runtime = 'python3.11'
        mock_metrics.metrics_data = {
            'sort_intensive': {
                'execution_time_ms': 25.5,
                'memory_used_mb': 50.0,
                'cold_start': True
            }
        }
        mock_metrics.send_cloudwatch_metrics.return_value = True
        mock_create_metrics.return_value = mock_metrics
        
        mock_process_workload.return_value = {
            'operation': 'sort_intensive',
            'data_size': 1000,
            'total_execution_time': 0.025
        }
        
        # Test event
        event = {
            'operation': 'sort_intensive',
            'data_size': 1000,
            'iterations': 1
        }
        
        # Call handler
        response = lambda_handler(event, self.mock_context)
        
        # Verify response
        self.assertEqual(response['statusCode'], 200)
        
        body = json.loads(response['body'])
        self.assertTrue(body['success'])
        self.assertEqual(body['operation'], 'sort_intensive')
        self.assertEqual(body['architecture'], 'x86_64')
        self.assertTrue(body['cold_start'])
        self.assertIn('processing_result', body)
        self.assertIn('performance_metrics', body)
        self.assertIn('function_info', body)
        
        # Verify mocks were called
        mock_create_metrics.assert_called_once()
        mock_process_workload.assert_called_once_with('sort_intensive', data_size=1000, iterations=1)
    
    @patch('lambda_function.create_metrics_collector')
    @patch('lambda_function.process_workload')
    def test_successful_api_gateway_invocation(self, mock_process_workload, mock_create_metrics):
        """Test successful API Gateway invocation."""
        # Setup mocks
        mock_metrics = Mock()
        mock_metrics.architecture = 'arm64'
        mock_metrics.function_name = 'test-function'
        mock_metrics.function_version = '1'
        mock_metrics.runtime = 'python3.11'
        mock_metrics.metrics_data = {
            'mathematical_computation': {
                'execution_time_ms': 15.2,
                'memory_used_mb': 30.0,
                'cold_start': False
            }
        }
        mock_metrics.send_cloudwatch_metrics.return_value = True
        mock_create_metrics.return_value = mock_metrics
        
        mock_process_workload.return_value = {
            'operation': 'mathematical_computation',
            'complexity': 500,
            'total_execution_time': 0.015
        }
        
        # Test API Gateway event
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({
                'operation': 'mathematical_computation',
                'complexity': 500,
                'iterations': 2
            }),
            'queryStringParameters': None
        }
        
        # Call handler
        response = lambda_handler(event, self.mock_context)
        
        # Verify response
        self.assertEqual(response['statusCode'], 200)
        
        body = json.loads(response['body'])
        self.assertTrue(body['success'])
        self.assertEqual(body['operation'], 'mathematical_computation')
        self.assertEqual(body['architecture'], 'arm64')
        
        # Verify mocks were called
        mock_process_workload.assert_called_once_with('mathematical_computation', complexity=500, iterations=2)
    
    def test_missing_operation_parameter(self):
        """Test error handling for missing operation parameter."""
        event = {
            'data_size': 1000
        }
        
        response = lambda_handler(event, self.mock_context)
        
        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertIn("Missing required parameter: 'operation'", body['error'])
    
    def test_invalid_operation(self):
        """Test error handling for invalid operation."""
        event = {
            'operation': 'invalid_operation'
        }
        
        response = lambda_handler(event, self.mock_context)
        
        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertIn("Invalid operation 'invalid_operation'", body['error'])
    
    @patch('lambda_function.create_metrics_collector')
    @patch('lambda_function.process_workload')
    def test_processing_error(self, mock_process_workload, mock_create_metrics):
        """Test error handling when processing fails."""
        # Setup mocks
        mock_metrics = Mock()
        mock_create_metrics.return_value = mock_metrics
        
        mock_process_workload.side_effect = Exception("Processing failed")
        
        event = {
            'operation': 'sort_intensive',
            'data_size': 1000
        }
        
        response = lambda_handler(event, self.mock_context)
        
        self.assertEqual(response['statusCode'], 500)
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertIn("Internal server error", body['error'])


class TestEventParsing(unittest.TestCase):
    """Test cases for event parsing functions."""
    
    def test_parse_direct_invocation_event(self):
        """Test parsing direct invocation event."""
        event = {
            'operation': 'sort_intensive',
            'data_size': 1000,
            'iterations': 1
        }
        
        parsed = parse_event(event)
        
        self.assertEqual(parsed['operation'], 'sort_intensive')
        self.assertEqual(parsed['data_size'], 1000)
        self.assertEqual(parsed['iterations'], 1)
        self.assertEqual(parsed['_event_type'], 'direct_invocation')
    
    def test_parse_api_gateway_event_with_body(self):
        """Test parsing API Gateway event with JSON body."""
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({
                'operation': 'mathematical_computation',
                'complexity': 500
            }),
            'queryStringParameters': {
                'iterations': '2'
            }
        }
        
        parsed = parse_event(event)
        
        self.assertEqual(parsed['operation'], 'mathematical_computation')
        self.assertEqual(parsed['complexity'], 500)
        self.assertEqual(parsed['iterations'], '2')  # Query params are strings
        self.assertEqual(parsed['_http_method'], 'POST')
        self.assertEqual(parsed['_event_type'], 'api_gateway')
    
    def test_parse_api_gateway_event_empty_body(self):
        """Test parsing API Gateway event with empty body."""
        event = {
            'httpMethod': 'GET',
            'body': None,
            'queryStringParameters': {
                'operation': 'string_processing',
                'text_size': '5000'
            }
        }
        
        parsed = parse_event(event)
        
        self.assertEqual(parsed['operation'], 'string_processing')
        self.assertEqual(parsed['text_size'], '5000')
        self.assertEqual(parsed['_http_method'], 'GET')
        self.assertEqual(parsed['_event_type'], 'api_gateway')
    
    def test_parse_api_gateway_event_invalid_json(self):
        """Test parsing API Gateway event with invalid JSON."""
        event = {
            'httpMethod': 'POST',
            'body': 'invalid json',
            'queryStringParameters': None
        }
        
        with self.assertRaises(ValueError) as context:
            parse_event(event)
        
        self.assertIn("Invalid JSON in request body", str(context.exception))


class TestInputValidation(unittest.TestCase):
    """Test cases for input validation functions."""
    
    def test_valid_sort_intensive_operation(self):
        """Test validation of valid sort_intensive operation."""
        event = {
            'operation': 'sort_intensive',
            'data_size': 5000,
            'iterations': 2
        }
        
        result = validate_input(event)
        
        self.assertTrue(result['valid'])
    
    def test_valid_mathematical_computation_operation(self):
        """Test validation of valid mathematical_computation operation."""
        event = {
            'operation': 'mathematical_computation',
            'complexity': 2000,
            'iterations': 1
        }
        
        result = validate_input(event)
        
        self.assertTrue(result['valid'])
    
    def test_invalid_data_size(self):
        """Test validation with invalid data_size."""
        event = {
            'operation': 'sort_intensive',
            'data_size': 200000,  # Too large
            'iterations': 1
        }
        
        result = validate_input(event)
        
        self.assertFalse(result['valid'])
        self.assertIn("data_size must be an integer between 1 and 100000", result['error'])
    
    def test_invalid_iterations(self):
        """Test validation with invalid iterations."""
        event = {
            'operation': 'string_processing',
            'text_size': 1000,
            'iterations': 15  # Too many
        }
        
        result = validate_input(event)
        
        self.assertFalse(result['valid'])
        self.assertIn("iterations must be an integer between 1 and 10", result['error'])
    
    def test_invalid_memory_size(self):
        """Test validation with invalid memory size."""
        event = {
            'operation': 'memory_intensive',
            'memory_size_mb': 200,  # Too large
            'iterations': 1
        }
        
        result = validate_input(event)
        
        self.assertFalse(result['valid'])
        self.assertIn("memory_size_mb must be an integer between 1 and 100", result['error'])


class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions."""
    
    def test_get_default_data_size(self):
        """Test getting default data sizes for operations."""
        self.assertEqual(get_default_data_size('sort_intensive'), 10000)
        self.assertEqual(get_default_data_size('mathematical_computation'), 1000)
        self.assertEqual(get_default_data_size('string_processing'), 10000)
        self.assertEqual(get_default_data_size('memory_intensive'), 10)
        self.assertEqual(get_default_data_size('unknown_operation'), 1000)
    
    def test_create_success_response(self):
        """Test creating success response."""
        data = {
            'operation': 'test',
            'result': 'success'
        }
        
        response = create_success_response(data)
        
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['headers']['Content-Type'], 'application/json')
        self.assertIn('Access-Control-Allow-Origin', response['headers'])
        
        body = json.loads(response['body'])
        self.assertEqual(body['operation'], 'test')
        self.assertEqual(body['result'], 'success')
    
    def test_create_error_response(self):
        """Test creating error response."""
        response = create_error_response(400, "Test error message")
        
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(response['headers']['Content-Type'], 'application/json')
        self.assertIn('Access-Control-Allow-Origin', response['headers'])
        
        body = json.loads(response['body'])
        self.assertFalse(body['success'])
        self.assertEqual(body['error'], "Test error message")
        self.assertEqual(body['statusCode'], 400)


class TestOperationParameterValidation(unittest.TestCase):
    """Test cases for operation-specific parameter validation."""
    
    def test_validate_sort_intensive_parameters(self):
        """Test validation of sort_intensive parameters."""
        # Valid parameters
        self.assertIsNone(validate_operation_parameters('sort_intensive', {
            'data_size': 5000,
            'iterations': 2
        }))
        
        # Invalid data_size
        error = validate_operation_parameters('sort_intensive', {
            'data_size': -1,
            'iterations': 1
        })
        self.assertIn("data_size must be an integer between 1 and 100000", error)
    
    def test_validate_mathematical_computation_parameters(self):
        """Test validation of mathematical_computation parameters."""
        # Valid parameters
        self.assertIsNone(validate_operation_parameters('mathematical_computation', {
            'complexity': 2000,
            'iterations': 1
        }))
        
        # Invalid complexity
        error = validate_operation_parameters('mathematical_computation', {
            'complexity': 20000,  # Too large
            'iterations': 1
        })
        self.assertIn("complexity must be an integer between 1 and 10000", error)
    
    def test_validate_string_processing_parameters(self):
        """Test validation of string_processing parameters."""
        # Valid parameters
        self.assertIsNone(validate_operation_parameters('string_processing', {
            'text_size': 15000,
            'iterations': 3
        }))
        
        # Invalid text_size
        error = validate_operation_parameters('string_processing', {
            'text_size': 0,  # Too small
            'iterations': 1
        })
        self.assertIn("text_size must be an integer between 1 and 100000", error)
    
    def test_validate_memory_intensive_parameters(self):
        """Test validation of memory_intensive parameters."""
        # Valid parameters
        self.assertIsNone(validate_operation_parameters('memory_intensive', {
            'memory_size_mb': 50,
            'iterations': 1
        }))
        
        # Invalid memory_size_mb
        error = validate_operation_parameters('memory_intensive', {
            'memory_size_mb': 150,  # Too large
            'iterations': 1
        })
        self.assertIn("memory_size_mb must be an integer between 1 and 100", error)


if __name__ == '__main__':
    unittest.main()