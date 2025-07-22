# Contributing to Lambda Performance Comparison

Thank you for your interest in contributing to the Lambda Performance Comparison project! This document provides guidelines and information for contributors.

## 🎯 Project Goals

This project aims to:
- Provide accurate performance comparisons between AWS Lambda architectures
- Demonstrate real-world serverless performance optimization techniques
- Serve as a reference implementation for Lambda performance testing
- Help developers make informed architecture decisions

## 🤝 How to Contribute

### Types of Contributions

We welcome various types of contributions:

- **Bug Reports**: Found an issue? Let us know!
- **Feature Requests**: Ideas for new workloads or improvements
- **Code Contributions**: Bug fixes, new features, or optimizations
- **Documentation**: Improvements to docs, examples, or guides
- **Performance Data**: Results from different regions or configurations

### Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/lambda-performance-comparison.git
   cd lambda-performance-comparison
   ```
3. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Set up development environment**:
   ```bash
   pip install -r requirements_test.txt
   sam build
   ```

## 🧪 Development Guidelines

### Code Style

- **Python**: Follow PEP 8 style guidelines
- **Type Hints**: Use type hints for all function parameters and returns
- **Docstrings**: Include comprehensive docstrings for all functions and classes
- **Comments**: Add comments for complex logic or performance-critical sections

### Code Structure

```
src/
├── lambda_function.py      # Main Lambda handler
├── data_processor.py       # Workload implementations
├── metrics.py             # Performance metrics collection
└── requirements.txt       # Python dependencies

tests/
├── test_lambda_function.py    # Handler tests
├── test_data_processor.py     # Workload tests
└── test_metrics.py           # Metrics tests

events/                    # Test event files
docs/                     # Documentation
```

### Testing Requirements

All contributions must include appropriate tests:

#### Unit Tests
```bash
# Run unit tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_data_processor.py -v
```

#### Local Integration Tests
```bash
# Test local SAM functionality
python local_test.py --direct

# Test API Gateway integration
sam local start-api --port 3000 &
python local_test.py --api
```

#### Performance Tests
```bash
# Validate performance test functionality
python performance_test.py
```

### Adding New Workloads

When adding new computational workloads:

1. **Implement in `data_processor.py`**:
   ```python
   def new_workload(self, param1: int, param2: str, iterations: int = 1) -> Dict[str, Any]:
       """
       Description of the workload and what it tests.
       
       Args:
           param1: Description
           param2: Description
           iterations: Number of iterations to run
           
       Returns:
           Dictionary with results and metadata
       """
   ```

2. **Add validation in `lambda_function.py`**:
   ```python
   elif operation == 'new_workload':
       # Add parameter validation
       # Add to valid_operations list
   ```

3. **Create test events**:
   ```json
   {
     "operation": "new_workload",
     "param1": 1000,
     "param2": "test_value",
     "iterations": 1
   }
   ```

4. **Add unit tests**:
   ```python
   def test_new_workload():
       processor = DataProcessor()
       result = processor.new_workload(1000, "test", 1)
       assert result['operation'] == 'new_workload'
       # Add more assertions
   ```

5. **Update documentation**:
   - Add to README.md operations section
   - Update API_REFERENCE.md
   - Add performance analysis if applicable

### Performance Considerations

When contributing performance-related code:

- **Consistency**: Ensure workloads are deterministic and repeatable
- **Scalability**: Test with various input sizes
- **Memory Efficiency**: Monitor memory usage patterns
- **Timing Accuracy**: Use `time.perf_counter()` for precise measurements
- **Architecture Neutrality**: Ensure workloads don't favor specific architectures

## 📝 Pull Request Process

### Before Submitting

1. **Run all tests**:
   ```bash
   python -m pytest tests/ -v
   python validate_local_setup.py
   sam validate
   ```

2. **Test locally**:
   ```bash
   sam build
   python local_test.py --direct
   ```

3. **Update documentation** if needed

4. **Check code style**:
   ```bash
   # Optional: Use black for formatting
   black src/ tests/
   
   # Optional: Use flake8 for linting
   flake8 src/ tests/
   ```

### Pull Request Template

When submitting a PR, please include:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Other (please describe)

## Testing
- [ ] Unit tests pass
- [ ] Local integration tests pass
- [ ] Manual testing completed
- [ ] Performance impact assessed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

### Review Process

1. **Automated Checks**: GitHub Actions will run tests
2. **Code Review**: Maintainers will review your code
3. **Testing**: Changes will be tested in various environments
4. **Merge**: Approved changes will be merged to main

## 🐛 Bug Reports

### Before Reporting

1. **Search existing issues** to avoid duplicates
2. **Test with latest version**
3. **Try local reproduction** if possible

### Bug Report Template

```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- AWS Region:
- SAM CLI Version:
- Python Version:
- Operating System:

## Additional Context
Logs, screenshots, or other relevant information
```

## 💡 Feature Requests

### Feature Request Template

```markdown
## Feature Description
Clear description of the proposed feature

## Use Case
Why is this feature needed?

## Proposed Solution
How should this feature work?

## Alternatives Considered
Other approaches you've considered

## Additional Context
Any other relevant information
```

## 📊 Performance Data Contributions

We welcome performance data from different:
- **AWS Regions**: Results may vary by region
- **Workload Variations**: Different parameter combinations
- **Time Periods**: Performance over time
- **Use Cases**: Real-world application scenarios

### Submitting Performance Data

1. **Use standardized format**:
   ```json
   {
     "test_date": "2025-01-15",
     "aws_region": "us-east-1",
     "test_iterations": 10,
     "results": {
       "sort_intensive": {
         "arm64_avg_ms": 225.5,
         "x86_avg_ms": 303.2,
         "improvement_pct": 25.6
       }
     }
   }
   ```

2. **Include methodology** and test conditions
3. **Verify reproducibility** of results

## 🔒 Security

### Reporting Security Issues

Please **DO NOT** report security vulnerabilities in public issues. Instead:

1. Email security concerns to: [security@yourproject.com]
2. Include detailed description and reproduction steps
3. Allow time for assessment and fix before disclosure

### Security Guidelines

- **No Secrets**: Never commit AWS credentials or secrets
- **Input Validation**: Validate all user inputs
- **Least Privilege**: Use minimal required permissions
- **Dependencies**: Keep dependencies updated

## 📚 Documentation Standards

### Code Documentation

- **Docstrings**: Use Google-style docstrings
- **Type Hints**: Include for all parameters and returns
- **Examples**: Provide usage examples where helpful

### README Updates

When updating documentation:
- Keep language clear and concise
- Include code examples
- Update table of contents if needed
- Test all provided commands

## 🏷️ Release Process

### Versioning

We use [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped
- [ ] Git tag created
- [ ] Release notes prepared

## 🤔 Questions?

- **General Questions**: [GitHub Discussions](https://github.com/your-username/lambda-performance-comparison/discussions)
- **Bug Reports**: [GitHub Issues](https://github.com/your-username/lambda-performance-comparison/issues)
- **Feature Requests**: [GitHub Issues](https://github.com/your-username/lambda-performance-comparison/issues)

## 🙏 Recognition

Contributors will be recognized in:
- **README.md**: Contributors section
- **Release Notes**: Major contributions highlighted
- **GitHub**: Contributor statistics

Thank you for helping make this project better! 🚀