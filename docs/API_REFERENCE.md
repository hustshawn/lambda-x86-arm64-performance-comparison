# API Reference

This document provides comprehensive API documentation for the Lambda Performance Comparison endpoints.

## Base URLs

- **ARM64 Endpoint**: `https://your-api-gateway-url/process-arm64`
- **x86_64 Endpoint**: `https://your-api-gateway-url/process-x86`

## Authentication

The API endpoints are publicly accessible and do not require authentication. In production environments, consider implementing:
- API Keys
- AWS IAM authentication
- Custom authorizers

## Request Format

All requests must use:
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Body**: JSON payload with operation parameters

## Response Format

All responses return JSON with the following structure:

```json
{
  "success": boolean,
  "operation": "string",
  "architecture": "arm64|x86_64",
  "cold_start": boolean,
  "processing_result": {},
  "performance_metrics": {},
  "function_info": {}
}
```

## Operations

### 1. Sort Intensive

Tests CPU performance with multiple sorting algorithms including quicksort, mergesort, heapsort, and built-in sort.

#### Request

```http
POST /process-arm64
Content-Type: application/json

{
  "operation": "sort_intensive",
  "data_size": 10000,
  "iterations": 1
}
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `operation` | string | Yes | - | Must be "sort_intensive" |
| `data_size` | integer | No | 10000 | Number of elements to sort (1-100000) |
| `iterations` | integer | No | 1 | Number of test iterations (1-10) |

#### Response

```json
{
  "success": true,
  "operation": "sort_intensive",
  "architecture": "arm64",
  "cold_start": false,
  "processing_result": {
    "operation": "sort_intensive",
    "data_size": 10000,
    "iterations": 1,
    "algorithms_tested": [
      {
        "iteration": 1,
        "quicksort_time": 0.0234,
        "mergesort_time": 0.0456,
        "heapsort_time": 0.0345,
        "builtin_time": 0.0123,
        "results_match": true
      }
    ],
    "total_execution_time": 0.1158,
    "timestamp": 1640995200.123
  },
  "performance_metrics": {
    "execution_time_ms": 115.8,
    "memory_used_mb": 45.2,
    "peak_memory_mb": 47.1,
    "memory_percent": 7.2,
    "cold_start": false,
    "data_size": 10000,
    "iterations": 1,
    "timestamp": "2025-01-15T10:30:00.123Z",
    "function_name": "ProcessorFunctionArm64",
    "function_version": "$LATEST",
    "runtime": "python3.11",
    "architecture": "arm64"
  },
  "function_info": {
    "function_name": "ProcessorFunctionArm64",
    "function_version": "$LATEST",
    "runtime": "python3.11",
    "architecture": "arm64"
  }
}
```

### 2. Mathematical Computation

Tests floating-point performance with pi calculation, matrix multiplication, prime generation, and high-precision arithmetic.

#### Request

```http
POST /process-x86
Content-Type: application/json

{
  "operation": "mathematical_computation",
  "complexity": 2000,
  "iterations": 1
}
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `operation` | string | Yes | - | Must be "mathematical_computation" |
| `complexity` | integer | No | 1000 | Computation complexity level (1-10000) |
| `iterations` | integer | No | 1 | Number of test iterations (1-10) |

#### Response

```json
{
  "success": true,
  "operation": "mathematical_computation",
  "architecture": "x86_64",
  "cold_start": false,
  "processing_result": {
    "operation": "mathematical_computation",
    "complexity": 2000,
    "iterations": 1,
    "computations": [
      {
        "iteration": 1,
        "pi_calculation": {
          "time": 0.0025,
          "result": 3.14159,
          "accuracy": 0.0001
        },
        "matrix_multiplication": {
          "time": 1.234,
          "matrix_size": 200,
          "result_sum": 12345.67
        },
        "prime_generation": {
          "time": 0.0123,
          "primes_found": 303,
          "largest_prime": 1999
        },
        "high_precision_factorial": {
          "time": 0.0001,
          "input": 20,
          "result_length": 19
        }
      }
    ],
    "total_execution_time": 1.2489,
    "timestamp": 1640995200.456
  },
  "performance_metrics": {
    "execution_time_ms": 1248.9,
    "memory_used_mb": 52.3,
    "peak_memory_mb": 54.1,
    "memory_percent": 8.1,
    "cold_start": false,
    "data_size": 1000,
    "iterations": 1,
    "timestamp": "2025-01-15T10:30:01.456Z",
    "function_name": "ProcessorFunctionX86",
    "function_version": "$LATEST",
    "runtime": "python3.11",
    "architecture": "x86_64"
  }
}
```

### 3. String Processing

Tests string manipulation performance with hashing, pattern matching, compression simulation, and text analysis.

#### Request

```http
POST /process-arm64
Content-Type: application/json

{
  "operation": "string_processing",
  "text_size": 15000,
  "iterations": 1
}
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `operation` | string | Yes | - | Must be "string_processing" |
| `text_size` | integer | No | 10000 | Size of text to process (1-100000) |
| `iterations` | integer | No | 1 | Number of test iterations (1-10) |

#### Response

```json
{
  "success": true,
  "operation": "string_processing",
  "architecture": "arm64",
  "cold_start": false,
  "processing_result": {
    "operation": "string_processing",
    "text_size": 15000,
    "iterations": 1,
    "processing_results": [
      {
        "iteration": 1,
        "hashing": {
          "time": 0.0123,
          "md5": "abc123...",
          "sha1": "def456...",
          "sha256": "ghi789...",
          "sha512": "jkl012..."
        },
        "pattern_matching": {
          "time": 0.0456,
          "pattern_1": {
            "pattern": "\\b\\w{4,}\\b",
            "matches_found": 1234,
            "unique_matches": 567
          },
          "total_matches": 2345,
          "replacements": {
            "total_replacements": 89,
            "final_text_length": 15089
          }
        },
        "compression": {
          "time": 0.0234,
          "original_length": 15000,
          "unique_characters": 45,
          "compression_ratio_estimate": 0.003,
          "most_frequent_char": " "
        },
        "text_analysis": {
          "time": 0.0345,
          "total_words": 2500,
          "unique_words": 890,
          "average_word_length": 5.2,
          "vocabulary_richness": 0.356
        }
      }
    ],
    "total_execution_time": 0.1158,
    "timestamp": 1640995200.789
  }
}
```

### 4. Memory Intensive

Tests memory allocation and access patterns with large array operations.

#### Request

```http
POST /process-x86
Content-Type: application/json

{
  "operation": "memory_intensive",
  "memory_size_mb": 25,
  "iterations": 1
}
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `operation` | string | Yes | - | Must be "memory_intensive" |
| `memory_size_mb` | integer | No | 10 | Memory size in MB to allocate (1-100) |
| `iterations` | integer | No | 1 | Number of test iterations (1-10) |

#### Response

```json
{
  "success": true,
  "operation": "memory_intensive",
  "architecture": "x86_64",
  "cold_start": false,
  "processing_result": {
    "operation": "memory_intensive",
    "memory_size_mb": 25,
    "iterations": 1,
    "memory_operations": [
      {
        "iteration": 1,
        "allocation_time": 0.234,
        "sequential_access_time": 0.123,
        "random_access_time": 0.456,
        "copy_time": 0.345,
        "sequential_sum": 12345678.9,
        "random_sum": 9876543.2,
        "arrays_equal": true
      }
    ],
    "total_execution_time": 1.158,
    "timestamp": 1640995201.012
  },
  "performance_metrics": {
    "execution_time_ms": 1158.0,
    "memory_used_mb": 78.5,
    "peak_memory_mb": 82.3,
    "memory_percent": 12.1,
    "cold_start": false,
    "data_size": 10,
    "iterations": 1,
    "timestamp": "2025-01-15T10:30:02.012Z",
    "function_name": "ProcessorFunctionX86",
    "function_version": "$LATEST",
    "runtime": "python3.11",
    "architecture": "x86_64"
  }
}
```

## Error Responses

### 400 Bad Request

Returned when request parameters are invalid:

```json
{
  "success": false,
  "error": "Invalid input: data_size must be an integer between 1 and 100000",
  "statusCode": 400
}
```

### 500 Internal Server Error

Returned when an unexpected error occurs:

```json
{
  "success": false,
  "error": "Internal server error: Unexpected error during processing",
  "statusCode": 500
}
```

## Performance Metrics

All responses include detailed performance metrics:

| Metric | Type | Description |
|--------|------|-------------|
| `execution_time_ms` | number | Total execution time in milliseconds |
| `memory_used_mb` | number | Memory usage in megabytes |
| `peak_memory_mb` | number | Peak memory usage in megabytes |
| `memory_percent` | number | Memory usage as percentage of available |
| `cold_start` | boolean | Whether this was a cold start invocation |
| `timestamp` | string | ISO 8601 timestamp of execution |

## Rate Limits

- **Concurrent Executions**: Limited by AWS Lambda concurrency limits
- **Request Rate**: No explicit rate limiting implemented
- **Timeout**: 30 seconds per request

## Best Practices

### Request Optimization

1. **Batch Operations**: Use `iterations` parameter for multiple runs
2. **Appropriate Sizing**: Choose realistic parameter values
3. **Error Handling**: Always check the `success` field

### Performance Testing

1. **Warm-up**: Run initial requests to warm up functions
2. **Multiple Samples**: Use multiple iterations for statistical significance
3. **Consistent Parameters**: Use identical parameters for architecture comparison

### Monitoring

1. **CloudWatch Metrics**: Monitor custom metrics in CloudWatch
2. **X-Ray Tracing**: Use AWS X-Ray for detailed performance analysis
3. **Cost Tracking**: Monitor execution costs in AWS Cost Explorer

## Examples

### cURL Examples

```bash
# Sort intensive test
curl -X POST https://your-api-gateway-url/process-arm64 \
     -H 'Content-Type: application/json' \
     -d '{"operation": "sort_intensive", "data_size": 5000, "iterations": 2}'

# Mathematical computation test
curl -X POST https://your-api-gateway-url/process-x86 \
     -H 'Content-Type: application/json' \
     -d '{"operation": "mathematical_computation", "complexity": 3000}'

# String processing test
curl -X POST https://your-api-gateway-url/process-arm64 \
     -H 'Content-Type: application/json' \
     -d '{"operation": "string_processing", "text_size": 20000}'

# Memory intensive test
curl -X POST https://your-api-gateway-url/process-x86 \
     -H 'Content-Type: application/json' \
     -d '{"operation": "memory_intensive", "memory_size_mb": 30}'
```

### Python Examples

```python
import requests
import json

# Performance comparison function
def compare_architectures(operation, params):
    arm64_url = "https://your-api-gateway-url/process-arm64"
    x86_url = "https://your-api-gateway-url/process-x86"
    
    payload = {"operation": operation, **params}
    
    # Test ARM64
    arm64_response = requests.post(arm64_url, json=payload)
    arm64_data = arm64_response.json()
    
    # Test x86_64
    x86_response = requests.post(x86_url, json=payload)
    x86_data = x86_response.json()
    
    # Compare results
    if arm64_data["success"] and x86_data["success"]:
        arm64_time = arm64_data["performance_metrics"]["execution_time_ms"]
        x86_time = x86_data["performance_metrics"]["execution_time_ms"]
        
        improvement = ((x86_time - arm64_time) / x86_time) * 100
        print(f"ARM64 is {improvement:.1f}% faster than x86_64")
    
    return arm64_data, x86_data

# Example usage
compare_architectures("sort_intensive", {"data_size": 8000})
```

### JavaScript Examples

```javascript
// Performance test function
async function testPerformance(architecture, operation, params) {
    const url = `https://your-api-gateway-url/process-${architecture}`;
    
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            operation: operation,
            ...params
        })
    });
    
    return await response.json();
}

// Example usage
async function compareArchitectures() {
    const params = { data_size: 5000, iterations: 1 };
    
    const arm64Result = await testPerformance('arm64', 'sort_intensive', params);
    const x86Result = await testPerformance('x86', 'sort_intensive', params);
    
    console.log('ARM64 time:', arm64Result.performance_metrics.execution_time_ms);
    console.log('x86_64 time:', x86Result.performance_metrics.execution_time_ms);
}
```

## Troubleshooting

### Common Issues

1. **Timeout Errors**: Reduce complexity or data size parameters
2. **Memory Errors**: Reduce memory_size_mb parameter
3. **Invalid Parameters**: Check parameter ranges and types
4. **Cold Start Delays**: First invocation may be slower

### Debug Information

Enable detailed logging by checking CloudWatch Logs for your Lambda functions:
- `/aws/lambda/ProcessorFunctionArm64`
- `/aws/lambda/ProcessorFunctionX86`