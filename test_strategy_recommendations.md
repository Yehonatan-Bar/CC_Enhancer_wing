# Test Strategy and Coverage Recommendations

## Current State Analysis

The project currently lacks a formal test suite for the newly added scripts (`fetch_url_content.py` and `get_file_content.py`). While the code includes robust error handling and security measures, there is no automated testing to verify these protections work as intended.

## Missing Test Coverage

### 1. fetch_url_content.py

#### Unit Tests Needed:

**URL Validation Function (`validate_url`)**
- [ ] Valid HTTP/HTTPS URLs
- [ ] Invalid schemes (ftp://, file://, javascript:)
- [ ] Empty/None inputs
- [ ] URLs exceeding length limit (>2048 chars)
- [ ] Missing netloc/hostname
- [ ] Private IP addresses (10.x.x.x, 192.168.x.x, 172.16-31.x.x)
- [ ] Loopback addresses (127.0.0.1, localhost)
- [ ] AWS metadata endpoint (169.254.169.254)
- [ ] Cloud metadata endpoints (metadata.google.internal, metadata.azure.com)
- [ ] IPv6 addresses (::1, fe80::, etc.)
- [ ] DNS rebinding scenarios
- [ ] Unicode/punycode URLs

**Private IP Detection (`is_private_ip`)**
- [ ] Various private IP ranges
- [ ] DNS resolution failures
- [ ] Hostnames resolving to private IPs
- [ ] Edge cases like 169.254.x.x

**Content Type Validation (`is_allowed_content_type`)**
- [ ] Allowed text types
- [ ] Blocked binary types
- [ ] Missing content-type header
- [ ] Malformed content-type headers

**Main Fetch Function (`fetch_url_content`)**
- [ ] Successful text content retrieval
- [ ] Binary content handling
- [ ] Timeout scenarios
- [ ] SSL certificate errors
- [ ] Connection errors
- [ ] HTTP error codes (404, 500, etc.)
- [ ] Redirect handling (especially redirect loops)
- [ ] Response size limits
- [ ] Content encoding issues
- [ ] Memory exhaustion protection
- [ ] Proxy errors
- [ ] Chunked transfer encoding

#### Integration Tests Needed:
- [ ] End-to-end CLI testing
- [ ] Interactive mode (user input)
- [ ] Command-line argument mode
- [ ] Various timeout configurations
- [ ] SSL verification toggle
- [ ] Verbose logging mode

### 2. get_file_content.py

#### Unit Tests Needed:

**Main Function (`get_file_content`)**
- [ ] Valid file reading
- [ ] Non-existent files
- [ ] Directory paths
- [ ] Symbolic links (safe and unsafe)
- [ ] Path traversal attempts (../, ..\)
- [ ] Absolute vs relative paths
- [ ] Files with special characters in names
- [ ] Large files exceeding size limit
- [ ] Binary file detection
- [ ] Various text encodings (UTF-8, Latin-1, etc.)
- [ ] Permission errors
- [ ] Empty files
- [ ] Files with null bytes

**Security Validations**
- [ ] Suspicious pattern detection ($, |, ;, etc.)
- [ ] Sensitive path blocking (/etc/, /root/, etc.)
- [ ] Windows sensitive paths
- [ ] Base path restriction enforcement
- [ ] Symlink security checks

**Type Validation**
- [ ] Invalid input types
- [ ] None handling
- [ ] Empty string handling

#### Integration Tests Needed:
- [ ] CLI argument parsing
- [ ] Exit code verification
- [ ] Error message formatting
- [ ] Base path restriction mode

## Test Framework Recommendations

### 1. Testing Stack
```
pytest==8.3.0
pytest-cov==5.0.0
pytest-mock==3.14.0
pytest-timeout==2.3.1
responses==0.25.0  # For mocking HTTP requests
```

### 2. Project Structure
```
code_enhancer/
├── src/
│   ├── fetch_url_content.py
│   └── get_file_content.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py  # Shared fixtures
│   ├── unit/
│   │   ├── test_fetch_url_content.py
│   │   └── test_get_file_content.py
│   └── integration/
│       ├── test_fetch_url_cli.py
│       └── test_get_file_cli.py
├── pytest.ini
└── .coveragerc
```

### 3. Example Test Implementation

```python
# tests/unit/test_fetch_url_content.py
import pytest
from unittest.mock import patch, Mock
import responses
from src.fetch_url_content import validate_url, is_private_ip, fetch_url_content

class TestURLValidation:
    """Test URL validation security checks."""
    
    @pytest.mark.parametrize("url,expected", [
        ("https://example.com", (True, None)),
        ("http://api.example.com/data", (True, None)),
        ("ftp://example.com", (False, "Only HTTP(S) URLs are allowed")),
        ("file:///etc/passwd", (False, "Only HTTP(S) URLs are allowed")),
        ("javascript:alert(1)", (False, "Only HTTP(S) URLs are allowed")),
        ("", (False, "URL cannot be empty")),
        (None, (False, "URL cannot be empty")),
        ("https://" + "a" * 2050, (False, "URL too long (max 2048 characters)")),
        ("https://192.168.1.1", (False, "Access to private/internal addresses is not allowed")),
        ("https://10.0.0.1", (False, "Access to private/internal addresses is not allowed")),
        ("https://127.0.0.1", (False, "Access to private/internal addresses is not allowed")),
        ("https://localhost", (False, "Access to private/internal addresses is not allowed")),
        ("https://169.254.169.254", (False, "Access to metadata endpoints is not allowed")),
        ("https://metadata.google.internal", (False, "Access to metadata endpoints is not allowed")),
    ])
    def test_url_validation(self, url, expected):
        """Test various URL validation scenarios."""
        with patch('socket.gethostbyname') as mock_dns:
            # Mock DNS resolution for private IPs
            if url and "192.168" in url:
                mock_dns.return_value = "192.168.1.1"
            elif url and "10.0" in url:
                mock_dns.return_value = "10.0.0.1"
            elif url and "localhost" in url:
                mock_dns.return_value = "127.0.0.1"
            else:
                mock_dns.return_value = "93.184.216.34"  # example.com
            
            result = validate_url(url)
            assert result == expected

class TestFetchContent:
    """Test content fetching functionality."""
    
    @responses.activate
    def test_successful_text_fetch(self):
        """Test successful text content retrieval."""
        responses.add(
            responses.GET,
            "https://example.com/data.json",
            json={"status": "ok"},
            status=200,
            content_type="application/json"
        )
        
        content, content_type, status = fetch_url_content("https://example.com/data.json")
        assert status == 200
        assert "application/json" in content_type
        assert '{"status": "ok"}' in content
    
    @responses.activate
    def test_size_limit_enforcement(self):
        """Test response size limit."""
        large_content = "x" * (11 * 1024 * 1024)  # 11MB
        responses.add(
            responses.GET,
            "https://example.com/large",
            body=large_content,
            status=200,
            headers={"Content-Length": str(len(large_content))}
        )
        
        with pytest.raises(ValueError, match="Response too large"):
            fetch_url_content("https://example.com/large", max_size=10*1024*1024)
```

### 4. Edge Cases and Security Tests

#### SSRF Protection Tests
- DNS rebinding attacks
- Time-of-check-time-of-use (TOCTOU) scenarios
- URL parser differences
- IPv6 private addresses
- Alternate IP representations (decimal, octal)

#### Path Traversal Tests
- Various OS path separators
- Unicode normalization attacks
- Null byte injection
- Double encoding
- Case sensitivity exploits

### 5. Performance and Stress Tests
- Concurrent request handling
- Memory usage under load
- Timeout accuracy
- Large file handling
- Network interruption recovery

## Implementation Priority

1. **High Priority** (Security Critical):
   - URL validation tests
   - Path traversal prevention tests
   - SSRF protection tests
   - Sensitive file access tests

2. **Medium Priority** (Functionality):
   - Content type handling
   - Encoding detection
   - Error handling paths
   - CLI argument parsing

3. **Low Priority** (Nice to Have):
   - Performance benchmarks
   - Stress tests
   - Cross-platform compatibility

## Coverage Goals
- Minimum 80% code coverage for all modules
- 100% coverage for security-critical functions
- All error paths must be tested
- Integration tests for all CLI commands

## CI/CD Integration

### GitHub Actions Workflow
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11, 3.12]
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    - name: Run tests with coverage
      run: |
        pytest --cov=src --cov-report=xml --cov-report=html
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## Security Testing Considerations

1. **Fuzzing**: Use hypothesis or similar property-based testing
2. **Static Analysis**: Integrate bandit for security linting
3. **Dependency Scanning**: Regular vulnerability checks
4. **Manual Penetration Testing**: Periodic security audits

## Maintenance Guidelines

1. Run tests before every commit
2. Maintain test documentation
3. Update tests when adding features
4. Review test coverage reports regularly
5. Keep test dependencies updated