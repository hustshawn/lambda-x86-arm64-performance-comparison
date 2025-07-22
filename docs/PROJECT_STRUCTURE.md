# Project Structure

This document outlines the professional organization of the Lambda Performance Comparison project.

## 📁 Directory Structure

```
lambda-performance-comparison/
├── README.md                    # Project overview and quick start
├── LICENSE                      # MIT license
├── CHANGELOG.md                 # Version history
├── CONTRIBUTING.md              # Contribution guidelines
├── DEPLOYMENT_GUIDE.md          # AWS deployment instructions
├── LOCAL_TESTING.md             # Local development guide
├── PERFORMANCE_RESULTS.md       # Latest performance benchmarks
├── template.yaml                # AWS SAM infrastructure template
├── samconfig.toml              # SAM CLI configuration
├── requirements_test.txt       # Development dependencies
└── .gitignore                  # Git ignore patterns

├── src/                        # Application source code
│   ├── lambda_function.py      # Main Lambda handler
│   ├── data_processor.py       # Computational workloads
│   ├── metrics.py              # Performance metrics collection
│   └── requirements.txt        # Runtime dependencies

├── tests/                      # Test suite
│   ├── test_lambda_function.py # Handler tests
│   ├── test_data_processor.py  # Workload tests
│   ├── test_metrics.py         # Metrics tests
│   ├── test_integration_metrics.py # Integration tests
│   └── test_performance_utilities.py # Performance test utilities

├── events/                     # Test event files
│   ├── direct-invocation-*.json # Direct Lambda invocation events
│   └── api-gateway-*.json      # API Gateway test events

├── scripts/                    # Development and testing utilities
│   ├── performance_test.py     # Production performance testing
│   ├── local_test.py          # Local development testing
│   └── validate_setup.py      # Project setup validation

├── config/                     # Configuration files
│   └── env.json               # Environment variables for local testing

├── docs/                       # Technical documentation
│   ├── API_REFERENCE.md       # Complete API documentation
│   ├── PERFORMANCE_ANALYSIS.md # Detailed performance analysis
│   └── PROJECT_STRUCTURE.md   # This file

└── .github/                    # GitHub integration
    ├── workflows/
    │   └── ci.yml             # CI/CD pipeline
    ├── ISSUE_TEMPLATE/
    │   ├── bug_report.md      # Bug report template
    │   └── feature_request.md # Feature request template
    └── PULL_REQUEST_TEMPLATE.md # PR template
```

## 🎯 Design Principles

### 1. **Separation of Concerns**
- **`src/`**: Production application code only
- **`tests/`**: Comprehensive test suite
- **`scripts/`**: Development and operational utilities
- **`config/`**: Configuration files
- **`docs/`**: Technical documentation

### 2. **Professional Organization**
- Clear directory hierarchy
- Logical grouping of related files
- Consistent naming conventions
- Minimal root directory clutter

### 3. **Development Workflow Support**
- Automated testing and validation
- Local development utilities
- CI/CD integration
- Comprehensive documentation

## 📋 File Categories

### Core Application (`src/`)
- **`lambda_function.py`**: Main entry point and event handling
- **`data_processor.py`**: Computational workload implementations
- **`metrics.py`**: Performance monitoring and CloudWatch integration
- **`requirements.txt`**: Runtime dependencies

### Testing (`tests/`)
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow validation
- **Performance Tests**: Metrics accuracy validation

### Development Tools (`scripts/`)
- **`performance_test.py`**: Production performance comparison
- **`local_test.py`**: Local development and testing automation
- **`validate_setup.py`**: Project setup and configuration validation

### Configuration (`config/`)
- **`env.json`**: Environment variables for local Lambda execution
- Centralized configuration management
- Environment-specific settings

### Documentation (`docs/`)
- **`API_REFERENCE.md`**: Complete API specification
- **`PERFORMANCE_ANALYSIS.md`**: Detailed performance methodology
- **`PROJECT_STRUCTURE.md`**: Project organization guide

### Infrastructure
- **`template.yaml`**: AWS SAM infrastructure as code
- **`samconfig.toml`**: SAM CLI deployment configuration
- **`.github/`**: GitHub Actions and templates

## 🚀 Usage Patterns

### Development Workflow
```bash
# 1. Setup and validation
python scripts/validate_setup.py

# 2. Local development
python scripts/local_test.py --direct

# 3. Build and deploy
sam build && sam deploy

# 4. Performance testing
python scripts/performance_test.py --arm64-url <url> --x86-url <url>
```

### Testing Workflow
```bash
# Unit tests
pytest tests/ -v

# Local integration tests
python scripts/local_test.py --api

# Setup validation
python scripts/validate_setup.py
```

## 🔧 Configuration Management

### Environment Variables
- **Local**: `config/env.json`
- **AWS**: Set via SAM template environment variables
- **CI/CD**: GitHub Actions environment variables

### SAM Configuration
- **Template**: `template.yaml` (infrastructure)
- **Config**: `samconfig.toml` (deployment parameters)
- **Events**: `events/*.json` (test data)

## 📊 Benefits of This Structure

### 1. **Maintainability**
- Clear separation of concerns
- Easy to locate and modify components
- Consistent organization patterns

### 2. **Scalability**
- Room for additional workloads in `src/data_processor.py`
- Extensible test suite in `tests/`
- Additional utilities can be added to `scripts/`

### 3. **Professional Standards**
- Industry-standard directory layout
- Comprehensive documentation
- Automated testing and validation

### 4. **Developer Experience**
- Clear entry points for different tasks
- Automated setup validation
- Comprehensive local testing support

## 🎯 Key Design Decisions

### Consolidated Scripts
- **Before**: Multiple scattered utility files in root
- **After**: Organized `scripts/` directory with clear purposes
- **Benefit**: Easier maintenance and discovery

### Centralized Configuration
- **Before**: Configuration files scattered in root
- **After**: Dedicated `config/` directory
- **Benefit**: Clear configuration management

### Comprehensive Documentation
- **Before**: Documentation mixed with code
- **After**: Dedicated `docs/` directory with structured content
- **Benefit**: Better information architecture

### Professional Testing
- **Before**: Ad-hoc testing scripts
- **After**: Comprehensive test suite with utilities
- **Benefit**: Reliable quality assurance

This structure supports professional software development practices while maintaining simplicity and clarity for contributors and users.