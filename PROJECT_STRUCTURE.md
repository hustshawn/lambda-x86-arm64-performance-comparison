# Project Structure

This document provides an overview of the Lambda Performance Comparison project structure and organization.

## 📁 Root Directory

```
lambda-performance-comparison/
├── README.md                    # Main project documentation
├── LICENSE                      # MIT license
├── CHANGELOG.md                 # Version history and changes
├── CONTRIBUTING.md              # Contribution guidelines
├── PROJECT_STRUCTURE.md         # This file
├── template.yaml                # AWS SAM template
├── samconfig.toml              # SAM CLI configuration
├── env.json                    # Environment variables for local testing
├── requirements_test.txt       # Testing and development dependencies
└── .gitignore                  # Git ignore patterns
```

## 📁 Source Code (`src/`)

```
src/
├── lambda_function.py          # Main Lambda handler
├── data_processor.py           # Computational workload implementations
├── metrics.py                  # Performance metrics collection
└── requirements.txt            # Lambda runtime dependencies
```

### Core Modules

- **`lambda_function.py`**: Main entry point for Lambda functions
  - Event parsing (API Gateway and direct invocation)
  - Input validation and error handling
  - Response formatting
  - Integration with data processor and metrics

- **`data_processor.py`**: Computational workload implementations
  - Sort intensive algorithms (quicksort, mergesort, heapsort)
  - Mathematical computations (pi calculation, matrix multiplication, primes)
  - String processing (hashing, pattern matching, text analysis)
  - Memory intensive operations (allocation, access patterns)

- **`metrics.py`**: Performance monitoring and metrics collection
  - High-precision timing with `time.perf_counter()`
  - Memory usage monitoring with `psutil`
  - CloudWatch custom metrics integration
  - Context managers for automatic measurement

## 📁 Tests (`tests/`)

```
tests/
├── test_lambda_function.py     # Lambda handler tests
├── test_data_processor.py      # Workload implementation tests
├── test_metrics.py             # Metrics collection tests
├── test_integration_metrics.py # Integration tests
└── test_performance_utilities.py # Performance testing utilities
```

### Test Categories

- **Unit Tests**: Individual function and class testing
- **Integration Tests**: End-to-end workflow testing
- **Performance Tests**: Validation of performance measurement accuracy
- **Mock Tests**: AWS service interaction testing

## 📁 Events (`events/`)

```
events/
├── direct-invocation-sort.json      # Direct Lambda invocation for sorting
├── direct-invocation-math.json      # Direct Lambda invocation for math
├── direct-invocation-string.json    # Direct Lambda invocation for strings
├── direct-invocation-memory.json    # Direct Lambda invocation for memory
├── api-gateway-sort.json           # API Gateway event for sorting
└── api-gateway-math.json           # API Gateway event for math
```

### Event Types

- **Direct Invocation**: JSON payloads for `sam local invoke`
- **API Gateway**: HTTP request simulation for `sam local start-api`

## 📁 Documentation (`docs/`)

```
docs/
├── API_REFERENCE.md            # Complete API documentation
└── PERFORMANCE_ANALYSIS.md     # Detailed performance analysis
```

### Documentation Types

- **API Reference**: Endpoint documentation, parameters, responses
- **Performance Analysis**: Test methodology, results, insights
- **Deployment Guide**: AWS deployment instructions
- **Local Testing**: Development and testing guide

## 📁 GitHub Configuration (`.github/`)

```
.github/
├── workflows/
│   └── ci.yml                  # GitHub Actions CI/CD pipeline
├── ISSUE_TEMPLATE/
│   ├── bug_report.md           # Bug report template
│   └── feature_request.md      # Feature request template
└── PULL_REQUEST_TEMPLATE.md    # Pull request template
```

### GitHub Features

- **CI/CD Pipeline**: Automated testing, validation, security scanning
- **Issue Templates**: Structured bug reports and feature requests
- **PR Template**: Standardized pull request format

## 📁 Testing and Utilities

```
├── local_test.py               # Local testing automation
├── performance_test.py         # Cloud performance testing
├── example_performance_test.py # Custom testing examples
└── validate_local_setup.py     # Setup validation
```

### Utility Scripts

- **Local Testing**: SAM CLI automation and validation
- **Performance Testing**: Automated architecture comparison
- **Setup Validation**: Environment and configuration checking
- **Examples**: Customizable testing scenarios

## 📁 Deployment and Configuration

```
├── DEPLOYMENT_GUIDE.md         # Deployment instructions
├── LOCAL_TESTING.md            # Local development guide
├── template.yaml               # SAM infrastructure template
├── samconfig.toml             # SAM CLI configuration
└── env.json                   # Local environment variables
```

### Configuration Files

- **SAM Template**: AWS infrastructure as code
- **SAM Config**: Deployment parameters and settings
- **Environment**: Local testing environment variables

## 📁 AWS SAM Build Artifacts (`.aws-sam/`)

```
.aws-sam/
├── build/                      # Built Lambda packages
├── cache/                      # SAM CLI cache
└── deps/                       # Python dependencies
```

*Note: This directory is generated by `sam build` and should not be committed to version control.*

## 🔧 Key Files Explained

### Infrastructure

- **`template.yaml`**: Defines AWS resources (Lambda functions, API Gateway, IAM roles)
- **`samconfig.toml`**: SAM CLI deployment configuration and parameters

### Application Code

- **`src/lambda_function.py`**: Main Lambda handler with event processing
- **`src/data_processor.py`**: Core computational workloads
- **`src/metrics.py`**: Performance measurement and CloudWatch integration

### Testing

- **`tests/`**: Comprehensive test suite with unit and integration tests
- **`events/`**: Sample events for local testing
- **`local_test.py`**: Automated local testing framework

### Documentation

- **`README.md`**: Project overview and quick start guide
- **`docs/API_REFERENCE.md`**: Complete API documentation
- **`docs/PERFORMANCE_ANALYSIS.md`**: Detailed performance results

## 🚀 Development Workflow

### 1. Local Development
```bash
# Setup
git clone <repository>
pip install -r requirements_test.txt

# Development
sam build
python local_test.py --direct
```

### 2. Testing
```bash
# Unit tests
pytest tests/ -v

# Integration tests
python validate_local_setup.py
```

### 3. Deployment
```bash
# Deploy to AWS
sam deploy --guided

# Test deployment
python performance_test.py
```

## 📊 Monitoring and Observability

### CloudWatch Integration
- Custom metrics namespace: `Lambda/PerformanceComparison`
- Metrics: ExecutionTime, MemoryUsage, ColdStart, PeakMemoryUsage
- Dimensions: Architecture, Operation, FunctionName

### X-Ray Tracing
- Enabled for both ARM64 and x86_64 functions
- Detailed performance analysis and service maps
- Request tracing and bottleneck identification

## 🔒 Security Considerations

### IAM Permissions
- Least privilege principle
- CloudWatch metrics publishing
- X-Ray tracing permissions

### Input Validation
- Parameter range validation
- Type checking
- Error handling

### Secrets Management
- No hardcoded credentials
- Environment variable configuration
- AWS IAM role-based access

## 📈 Performance Monitoring

### Metrics Collection
- High-precision timing measurements
- Memory usage monitoring
- Cold start detection
- Architecture-specific metrics

### Analysis Tools
- Automated performance comparison
- Statistical analysis
- Cost-performance calculations
- Trend analysis capabilities

## 🤝 Contributing

### Code Organization
- Modular design with clear separation of concerns
- Comprehensive test coverage
- Type hints and documentation
- Consistent code style

### Development Standards
- PEP 8 compliance
- Type annotations
- Comprehensive docstrings
- Unit test coverage

This project structure supports scalable development, comprehensive testing, and production deployment while maintaining clear organization and documentation.