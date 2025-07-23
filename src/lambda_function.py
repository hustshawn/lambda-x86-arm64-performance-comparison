"""
Lambda function handler for performance comparison between ARM64 and x86_64 architectures.

This handler processes both API Gateway and direct invocation events, integrates data processing
with performance metrics collection, and provides comprehensive error handling.
"""

import json
import os
import logging
import traceback
from typing import Dict, Any, Optional, Union

# Import our custom modules
from data_processor import process_workload
from metrics import create_metrics_collector, MetricsContext

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Global variables for cold start detection
_cold_start = True
_metrics_collector = None


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda function handler for performance comparison.

    Processes both API Gateway and direct invocation events, runs data processing
    workloads with performance metrics collection.

    Args:
        event: Lambda event (API Gateway or direct invocation)
        context: Lambda context object

    Returns:
        Response dictionary with results and performance metrics
    """
    global _cold_start, _metrics_collector

    # Initialize metrics collector on first invocation
    if _metrics_collector is None:
        architecture = os.environ.get("ARCHITECTURE", "unknown")
        function_name = context.function_name if context else "unknown"
        _metrics_collector = create_metrics_collector(
            architecture=architecture, function_name=function_name
        )

    # Detect cold start
    is_cold_start = _cold_start
    _cold_start = False

    try:
        # Parse the incoming event
        parsed_event = parse_event(event)
        logger.info(f"Parsed event: {json.dumps(parsed_event, indent=2)}")

        # Validate input parameters
        validation_result = validate_input(parsed_event)
        if not validation_result["valid"]:
            return create_error_response(400, validation_result["error"])

        # Extract operation parameters
        operation = parsed_event["operation"]
        data_size = parsed_event.get("data_size", get_default_data_size(operation))
        iterations = parsed_event.get("iterations", 1)

        # Extract operation-specific parameters based on operation type
        operation_params = {}
        if operation == "sort_intensive":
            operation_params["data_size"] = data_size
            operation_params["iterations"] = iterations
        elif operation == "mathematical_computation":
            operation_params["complexity"] = parsed_event.get("complexity", 1000)
            operation_params["iterations"] = iterations
        elif operation == "string_processing":
            operation_params["text_size"] = parsed_event.get("text_size", 10000)
            operation_params["iterations"] = iterations
        elif operation == "memory_intensive":
            operation_params["memory_size_mb"] = parsed_event.get("memory_size_mb", 10)
            operation_params["iterations"] = iterations

        logger.info(
            f"Processing operation: {operation} with params: {operation_params}"
        )

        # Process the workload with metrics collection
        with MetricsContext(
            _metrics_collector,
            operation,
            data_size=data_size,
            iterations=iterations,
            cold_start=is_cold_start,
        ):

            # Run the data processing workload
            processing_result = process_workload(operation, **operation_params)

        # Get collected metrics
        operation_metrics = _metrics_collector.metrics_data.get(operation, {})

        # Send metrics to CloudWatch (best effort)
        try:
            _metrics_collector.send_cloudwatch_metrics(operation)
        except Exception as e:
            logger.warning(f"Failed to send CloudWatch metrics: {e}")

        # Prepare response
        response_data = {
            "success": True,
            "operation": operation,
            "architecture": _metrics_collector.architecture,
            "cold_start": is_cold_start,
            "processing_result": processing_result,
            "performance_metrics": operation_metrics,
            "function_info": {
                "function_name": _metrics_collector.function_name,
                "function_version": _metrics_collector.function_version,
                "runtime": _metrics_collector.runtime,
                "architecture": _metrics_collector.architecture,
            },
        }

        logger.info(f"Operation completed successfully: {operation}")
        return create_success_response(response_data)

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return create_error_response(400, f"Invalid input: {str(e)}")

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return create_error_response(500, f"Internal server error: {str(e)}")


def parse_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse incoming Lambda event (API Gateway or direct invocation).

    Args:
        event: Raw Lambda event

    Returns:
        Parsed event dictionary

    Raises:
        ValueError: If event format is invalid
    """
    # Check if this is an API Gateway event
    if "httpMethod" in event and "body" in event:
        return parse_api_gateway_event(event)
    else:
        return parse_direct_invocation_event(event)


def parse_api_gateway_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse API Gateway event.

    Args:
        event: API Gateway event

    Returns:
        Parsed event dictionary
    """
    try:
        # Parse JSON body
        if event.get("body"):
            if isinstance(event["body"], str):
                body = json.loads(event["body"])
            else:
                body = event["body"]
        else:
            body = {}

        # Extract query parameters
        query_params = event.get("queryStringParameters") or {}

        # Merge body and query parameters (body takes precedence)
        parsed_event = {**query_params, **body}

        # Add HTTP method info
        parsed_event["_http_method"] = event.get("httpMethod", "POST")
        parsed_event["_event_type"] = "api_gateway"

        return parsed_event

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in request body: {e}")


def parse_direct_invocation_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse direct Lambda invocation event.

    Args:
        event: Direct invocation event

    Returns:
        Parsed event dictionary
    """
    parsed_event = dict(event)
    parsed_event["_event_type"] = "direct_invocation"
    return parsed_event


def validate_input(parsed_event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate input parameters.

    Args:
        parsed_event: Parsed event dictionary

    Returns:
        Validation result with 'valid' boolean and 'error' message if invalid
    """
    # Check required operation parameter
    if "operation" not in parsed_event:
        return {"valid": False, "error": "Missing required parameter: 'operation'"}

    operation = parsed_event["operation"]

    # Validate operation type
    valid_operations = [
        "sort_intensive",
        "mathematical_computation",
        "string_processing",
        "memory_intensive",
    ]

    if operation not in valid_operations:
        return {
            "valid": False,
            "error": f"Invalid operation '{operation}'. Valid operations: {valid_operations}",
        }

    # Validate operation-specific parameters
    validation_error = validate_operation_parameters(operation, parsed_event)
    if validation_error:
        return {"valid": False, "error": validation_error}

    return {"valid": True}


def validate_operation_parameters(
    operation: str, parsed_event: Dict[str, Any]
) -> Optional[str]:
    """
    Validate operation-specific parameters.

    Args:
        operation: Operation name
        parsed_event: Parsed event dictionary

    Returns:
        Error message if validation fails, None if valid
    """
    try:
        if operation == "sort_intensive":
            data_size = parsed_event.get("data_size", 10000)
            if not isinstance(data_size, int) or data_size < 1 or data_size > 100000:
                return "data_size must be an integer between 1 and 100000"

        elif operation == "mathematical_computation":
            complexity = parsed_event.get("complexity", 1000)
            if not isinstance(complexity, int) or complexity < 1 or complexity > 10000:
                return "complexity must be an integer between 1 and 10000"

        elif operation == "string_processing":
            text_size = parsed_event.get("text_size", 10000)
            if not isinstance(text_size, int) or text_size < 1 or text_size > 100000:
                return "text_size must be an integer between 1 and 100000"

        elif operation == "memory_intensive":
            memory_size_mb = parsed_event.get("memory_size_mb", 10)
            if (
                not isinstance(memory_size_mb, int)
                or memory_size_mb < 1
                or memory_size_mb > 100
            ):
                return "memory_size_mb must be an integer between 1 and 100"

        # Validate common parameters
        iterations = parsed_event.get("iterations", 1)
        if not isinstance(iterations, int) or iterations < 1 or iterations > 10:
            return "iterations must be an integer between 1 and 10"

    except (TypeError, ValueError) as e:
        return f"Parameter validation error: {e}"

    return None


def get_default_data_size(operation: str) -> int:
    """
    Get default data size for an operation.

    Args:
        operation: Operation name

    Returns:
        Default data size
    """
    defaults = {
        "sort_intensive": 10000,
        "mathematical_computation": 1000,
        "string_processing": 10000,
        "memory_intensive": 10,
    }
    return defaults.get(operation, 1000)


def create_success_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create successful response.

    Args:
        data: Response data

    Returns:
        Formatted response dictionary
    """
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
        },
        "body": json.dumps(data, indent=2, default=str),
    }


def create_error_response(status_code: int, error_message: str) -> Dict[str, Any]:
    """
    Create error response.

    Args:
        status_code: HTTP status code
        error_message: Error message

    Returns:
        Formatted error response dictionary
    """
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
        },
        "body": json.dumps(
            {"success": False, "error": error_message, "statusCode": status_code},
            indent=2,
        ),
    }
