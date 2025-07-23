# 🚀 AWS Lambda Performance Comparison: ARM64 vs x86_64

A comprehensive serverless application that compares performance between AWS Lambda ARM64 (Graviton2) and x86_64 architectures across various computational workloads.

[![AWS](https://img.shields.io/badge/AWS-Lambda-orange)](https://aws.amazon.com/lambda/)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![SAM](https://img.shields.io/badge/AWS-SAM-green)](https://aws.amazon.com/serverless/sam/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Overview

This project provides a real-world performance comparison between AWS Lambda's ARM64 (Graviton2) and x86_64 architectures using identical Python 3.11 runtime environments. It includes four different computational workloads designed to stress different aspects of processor performance:

- **Sort Intensive**: CPU-intensive sorting algorithms
- **Mathematical Computation**: Floating-point and matrix operations
- **String Processing**: Text manipulation and pattern matching
- **Memory Intensive**: Large data allocation and memory access patterns

## 🎯 Key Features

- **Dual Architecture Deployment**: Identical Lambda functions on both ARM64 and x86_64
- **Comprehensive Workloads**: Four different test scenarios covering various performance aspects
- **Real-time Metrics**: CloudWatch integration with custom performance metrics
- **API Gateway Integration**: RESTful endpoints for easy testing
- **Local Testing Support**: Complete SAM CLI local development environment
- **Performance Analytics**: Automated comparison and analysis tools
- **Cost Optimization**: Demonstrates price-performance benefits of Graviton2

## 📊 Performance Results

**Latest Test Results (July 22, 2025)** - Based on comprehensive testing in production AWS Lambda environment:

| Workload Type | ARM64 Performance Advantage | Test Details |
|---------------|----------------------------|--------------|
| **Mathematical Computation** | **🏆 34.3% faster** | 4,062ms vs 6,186ms |
| **String Processing** | **🏆 34.2% faster** | 12.7ms vs 19.3ms |
| **Sort Intensive** | **🏆 25.8% faster** | 230ms vs 310ms |
| **Memory Intensive** | **🏆 11.8% faster** | 1,850ms vs 2,098ms |

**🎯 Final Score: ARM64: 4 | x86_64: 0**

### Performance Visualization

```
Mathematical Computation:  ARM64 ████████████████████████████████████ 34.3% faster
String Processing:         ARM64 ████████████████████████████████████ 34.2% faster  
Sort Intensive:            ARM64 ██████████████████████████ 25.8% faster
Memory Intensive:          ARM64 ████████████ 11.8% faster
```

> **💰 Cost Impact**: Combined with 20% lower ARM64 pricing, total cost savings range from **35-45%**

*View detailed results in [PERFORMANCE_RESULTS.md](PERFORMANCE_RESULTS.md)*

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   API Gateway   │────│  Lambda ARM64    │────│   CloudWatch    │
│                 │    │  (Graviton2)     │    │   Metrics       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │              
         │              ┌──────────────────┐    ┌─────────────────┐
         └──────────────│  Lambda x86_64   │────│   X-Ray         │
                        │                  │    │   Tracing       │
                        └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- AWS CLI configured with appropriate permissions
- AWS SAM CLI installed
- Python 3.11+
- Docker (for local testing)

### 1. Clone and Deploy

```bash
# Clone the repository
git clone https://github.com/your-username/lambda-performance-comparison.git
cd lambda-performance-comparison

# Build the application
sam build

# Deploy to AWS
sam deploy --guided
```

### 2. Test the Deployment

```bash
# Test ARM64 endpoint
curl -X POST https://your-api-gateway-url/process-arm64 \
     -H 'Content-Type: application/json' \
     -d '{"operation": "sort_intensive", "data_size": 5000}'

# Test x86_64 endpoint  
curl -X POST https://your-api-gateway-url/process-x86 \
     -H 'Content-Type: application/json' \
     -d '{"operation": "mathematical_computation", "complexity": 2000}'
```

### 3. Run Performance Comparison

```bash
# Run comprehensive performance test (auto-detects URLs from SAM stack)
python scripts/performance_test.py

# Or specify URLs manually if needed
python scripts/performance_test.py --arm64-url <your-arm64-url> --x86-url <your-x86-url>
```

## 📚 Documentation

### Core Documentation
- **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation and usage examples
- **[Performance Analysis](docs/PERFORMANCE_ANALYSIS.md)** - Detailed methodology and comprehensive results
- **[Performance Results](PERFORMANCE_RESULTS.md)** - Latest test results and benchmarks
- **[Project Structure](docs/PROJECT_STRUCTURE.md)** - Professional project organization guide

### Development & Deployment
- **[Deployment Guide](DEPLOYMENT_GUIDE.md)** - AWS deployment instructions and configuration
- **[Local Development](LOCAL_TESTING.md)** - Local testing and development workflow
- **[Contributing Guide](CONTRIBUTING.md)** - Contribution guidelines and development standards

## 🧪 Available Operations

### Sort Intensive
Tests CPU performance with multiple sorting algorithms:
```json
{
  "operation": "sort_intensive",
  "data_size": 10000,
  "iterations": 1
}
```

### Mathematical Computation
Tests floating-point performance and mathematical operations:
```json
{
  "operation": "mathematical_computation",
  "complexity": 2000,
  "iterations": 1
}
```

### String Processing
Tests string manipulation and pattern matching:
```json
{
  "operation": "string_processing",
  "text_size": 15000,
  "iterations": 1
}
```

### Memory Intensive
Tests memory allocation and access patterns:
```json
{
  "operation": "memory_intensive",
  "memory_size_mb": 25,
  "iterations": 1
}
```

## 📈 Monitoring and Metrics

The application automatically sends custom metrics to CloudWatch:

- **ExecutionTime**: Function execution time in milliseconds
- **MemoryUsage**: Memory consumption in megabytes
- **ColdStart**: Cold start occurrences
- **PeakMemoryUsage**: Peak memory usage during execution

Access metrics in CloudWatch under the `Lambda/PerformanceComparison` namespace.

## 🛠️ Local Development

### Setup Local Environment

```bash
# Install dependencies
pip install -r requirements_test.txt

# Validate project setup
python scripts/validate_setup.py

# Build for local testing
sam build
```

### Run Local Tests

```bash
# Direct Lambda invocation
sam local invoke ProcessorFunctionArm64 --event events/direct-invocation-sort.json

# Automated local testing
python scripts/local_test.py --direct

# Local API Gateway testing
sam local start-api --port 3000
python scripts/local_test.py --api
```

## 🔧 Configuration

### Environment Variables

- `ARCHITECTURE`: Set automatically (arm64 or x86_64)
- `PYTHONPATH`: Python module path configuration

### SAM Template Parameters

- `Stage`: Deployment stage (default: dev)

### Function Configuration

- **Runtime**: Python 3.11
- **Memory**: 512 MB (configurable)
- **Timeout**: 30 seconds (configurable)
- **Tracing**: AWS X-Ray enabled

## 💰 Cost Considerations

ARM64 (Graviton2) typically provides:
- **Up to 34% better price-performance** for compute-intensive workloads
- **Lower execution costs** due to faster processing
- **Reduced memory usage** in some scenarios

Monitor actual costs using AWS Cost Explorer and compare price per execution.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on:

- Code style and standards
- Testing requirements
- Pull request process
- Issue reporting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- AWS Lambda team for Graviton2 support
- AWS SAM team for excellent tooling
- Python community for performance optimization insights

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/lambda-performance-comparison/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/lambda-performance-comparison/discussions)
- **AWS Documentation**: [Lambda Performance](https://docs.aws.amazon.com/lambda/latest/dg/performance.html)

## 🔗 Related Projects

- [AWS Lambda Powertools](https://github.com/awslabs/aws-lambda-powertools-python)
- [AWS SAM Examples](https://github.com/aws/aws-sam-cli-app-templates)
- [Serverless Performance Patterns](https://serverlessland.com/patterns)

---

**⭐ If this project helped you understand Lambda performance characteristics, please give it a star!**