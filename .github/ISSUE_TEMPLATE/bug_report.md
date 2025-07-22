---
name: Bug report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''

---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Deploy with '...'
2. Call endpoint with '....'
3. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Actual behavior**
What actually happened instead.

**Environment**
- AWS Region: [e.g. us-east-1]
- SAM CLI Version: [e.g. 1.100.0]
- Python Version: [e.g. 3.11]
- Operating System: [e.g. macOS, Windows, Linux]

**Request/Response**
If applicable, add the request payload and response that caused the issue:

```json
// Request
{
  "operation": "sort_intensive",
  "data_size": 5000
}

// Response
{
  "success": false,
  "error": "..."
}
```

**Logs**
If applicable, add CloudWatch logs or local execution logs:

```
[ERROR] 2025-01-15T10:30:00.123Z RequestId: abc-123 Error message here
```

**Additional context**
Add any other context about the problem here.

**Checklist**
- [ ] I have searched existing issues to avoid duplicates
- [ ] I have tested with the latest version
- [ ] I have included all relevant information above