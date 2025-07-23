# Local Testing Guide

This guide explains how to test the Lambda Performance Comparison application locally using AWS SAM CLI.

## Prerequisites

- AWS SAM CLI installed and configured
- Docker installed and running
- Python 3.11 or later
- Required Python packages: `requests`
- AWS CLI configured (for automatic URL detection in performance tests)

## Quick Start

1. **Build the application:**
   ```bash
   sam build
   ```

2. **Run automated tests:**
   ```bash
   # Direct invocation tests
   python local_test.py --direct
   
   # API Gateway tests (requires separate terminal for API server)
   sam local start-api --port 3000 &
   python local_test.py --api
   ```

## Testing Methods

### 1. Direct Lambda Invocation

Test Lambda functions directly without API Gateway:

```bash
# Test ARM64 function with sorting workload
sam local invoke ProcessorFunctionArm64 --event events/direct-invocation-sort.json

# Test x86_64 function with mathematical computation
sam local invoke ProcessorFunctionX86 --event events/direct-invocation-math.json

# Test with custom event
echo '{"operation": "string_processing", "text_size": 20000}' | sam local invoke ProcessorFunctionArm64
```

### 2. API Gateway Local Testing

Start the local API Gateway server:

```bash
sam local start-api --port 3000
```

Test endpoints with curl:

```bash
# Test ARM64 endpoint
curl -X POST http://localhost:3000/process-arm64 \
     -H 'Content-Type: application/json' \
     -d '{"operation": "sort_intensive", "data_size": 8000}'

# Test x86_64 endpoint  
curl -X POST http://localhost:3000/process-x86 \
     -H 'Content-Type: application/json' \
     -d '{"operation": "mathematical_computation", "complexity": 3000}'
```

### 3. Automated Testing Script

Use the provided testing script for comprehensive testing:

```bash
# Show usage instructions
python local_test.py --help

# Run direct invocation tests
python local_test.py --direct

# Run API Gateway tests (requires API server running)
python local_test.py --api
```

## Available Test Events

### Direct Invocation Events

- `events/direct-invocation-sort.json` - Sorting algorithm test
- `events/direct-invocation-math.json` - Mathematical computation test  
- `events/direct-invocation-string.json` - String processing test
- `events/direct-invocation-memory.json` - Memory intensive test

### API Gateway Events

- `events/api-gateway-sort.json` - API Gateway sorting test
- `events/api-gateway-math.json` - API Gateway math test

## Test Operations

### Sort Intensive
```json
{
  "operation": "sort_intensive",
  "data_size": 10000,
  "iterations": 1
}
```

### Mathematical Computation
```json
{
  "operation": "mathematical_computation", 
  "complexity": 2000,
  "iterations": 1
}
```

### String Processing
```json
{
  "operation": "string_processing",
  "text_size": 15000,
  "iterations": 1
}
```

### Memory Intensive
```json
{
  "operation": "memory_intensive",
  "memory_size_mb": 25,
  "iterations": 1
}
```

## Configuration Files

### SAM Configuration (`samconfig.toml`)

The SAM configuration file includes settings for:
- Build parameters with caching enabled
- Deploy parameters with stack configuration
- Local testing parameters with warm containers
- Debug configuration for development

### Environment Variables (`env.json`)

Local environment variables for each function:
- `ARCHITECTURE`: Set to "arm64" or "x86_64"
- `PYTHONPATH`: Python module path configuration

## Debugging

### Enable Debug Mode

Start functions with debugging enabled:

```bash
# Direct invocation with debugging
sam local invoke ProcessorFunctionArm64 \
    --event events/direct-invocation-sort.json \
    --debug-port 5858 \
    --debug-args "-e debugpy -e listen=0.0.0.0:5858 -e wait_for_client=y"

# API Gateway with debugging
sam local start-api --debug-port 5858 \
    --debug-args "-e debugpy -e listen=0.0.0.0:5858 -e wait_for_client=y"
```

### View Logs

SAM CLI outputs logs directly to the console. For structured log analysis:

```bash
# Save logs to file
sam local invoke ProcessorFunctionArm64 \
    --event events/direct-invocation-sort.json 2>&1 | tee test-logs.txt
```

## Performance Comparison

### Local vs Cloud Performance

Note that local testing performance will differ from cloud execution:

- **Local**: Uses your machine's architecture and resources
- **Cloud**: Uses actual AWS Lambda ARM64/x86_64 instances

### Comparing Architectures Locally

While you can't truly compare ARM64 vs x86_64 locally (unless you have both architectures), you can:

1. Test function logic and correctness
2. Validate input/output formats
3. Test error handling
4. Verify metrics collection
5. Ensure API Gateway integration works

## Troubleshooting

### Common Issues

1. **Docker not running**: Ensure Docker is installed and running
2. **Port conflicts**: Change the port if 3000 is in use: `--port 3001`
3. **Module import errors**: Check `PYTHONPATH` in `env.json`
4. **Timeout errors**: Increase timeout in `template.yaml` for complex operations

### Validation Commands

```bash
# Validate SAM template
sam validate

# Check Docker
docker --version

# Check SAM CLI
sam --version

# Test Python imports
python -c "import sys; print(sys.path)"
```

## Integration with Development Workflow

### Pre-deployment Testing

Always test locally before deploying:

```bash
# 1. Build
sam build

# 2. Test locally
python local_test.py --direct

# 3. Deploy to AWS
sam deploy --guided
```

### Performance Testing (Post-Deployment)

After deploying to AWS, you can run comprehensive performance comparisons:

```bash
# Automatic URL detection from SAM stack
python scripts/performance_test.py

# Run specific operation only
python scripts/performance_test.py --operation mathematical_computation

# Save results to file
python scripts/performance_test.py --output performance_results.json

# Run with custom iterations
python scripts/performance_test.py --iterations 5

# Manual URL specification (if auto-detection fails)
python scripts/performance_test.py \
    --arm64-url https://your-api-gateway-url/dev/process-arm64 \
    --x86-url https://your-api-gateway-url/dev/process-x86
```

The performance test script automatically:
- Reads your `samconfig.toml` for stack name and region
- Fetches endpoint URLs from CloudFormation stack outputs
- Runs comprehensive tests across all operation types
- Provides detailed performance analysis and comparison

### Continuous Testing

Set up automated testing in your development workflow:

```bash
#!/bin/bash
# test-script.sh
set -e

echo "Building SAM application..."
sam build

echo "Running local tests..."
python scripts/local_test.py --direct

echo "Deploying to AWS..."
sam deploy

echo "Running performance comparison..."
python scripts/performance_test.py --quiet

echo "All tests passed! Deployment successful."
```

This local testing setup provides comprehensive validation of your Lambda functions before and after deployment to AWS.