# Backend Test Suite

Comprehensive test suite for the Smart Voice Interviewer backend API.

## 📋 Test Coverage

### Test Files

1. **test_database.py** - Database Layer Tests
   - User management (create, read, update)
   - Authentication and password hashing
   - Interview history tracking
   - Statistics and achievements
   - Connection management

2. **test_auth.py** - Authentication Tests
   - User registration
   - Login with username/email
   - JWT token generation and validation
   - Protected route access
   - Token security

3. **test_interview.py** - Interview Flow Tests
   - Starting interviews
   - Answer submission and scoring
   - Semantic similarity evaluation
   - Session management
   - Course recommendations

4. **test_profile.py** - Profile & Stats Tests
   - Profile retrieval and updates
   - Statistics tracking
   - Interview history
   - Analytics and trends
   - Achievement tracking

5. **test_general.py** - General Endpoint Tests
   - Health checks
   - Categories listing
   - Statistics endpoint
   - CORS configuration
   - Error handling
   - Rate limiting

## 🚀 Running Tests

### Prerequisites

1. **Install Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Set Up Test Database** (Optional for unit tests)
   ```bash
   # Create a test PostgreSQL database
   createdb test_interview_db
   
   # Or use Docker
   docker run -d --name test-postgres \
     -e POSTGRES_USER=test_user \
     -e POSTGRES_PASSWORD=test_password \
     -e POSTGRES_DB=test_interview_db \
     -p 5432:5432 postgres:15
   ```

3. **Configure Test Environment**
   ```bash
   # Copy and edit .env.test
   cp .env.test.example .env.test
   ```

### Run All Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov

# Run with HTML coverage report
pytest --cov --cov-report=html
```

### Run Specific Tests

```bash
# Run specific test file
pytest tests/test_database.py

# Run specific test class
pytest tests/test_auth.py::TestRegistration

# Run specific test function
pytest tests/test_auth.py::TestRegistration::test_register_success

# Run tests matching a pattern
pytest -k "test_register"
```

### Run by Markers

```bash
# Run only unit tests (no database required)
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only database tests
pytest -m database

# Run only authentication tests
pytest -m auth

# Run all except slow tests
pytest -m "not slow"
```

### Windows PowerShell

```powershell
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov --cov-report=html

# Run specific file
python -m pytest tests/test_database.py
```

## 📊 Test Markers

- `@pytest.mark.unit` - Unit tests (fast, no external dependencies)
- `@pytest.mark.integration` - Integration tests (require API/database)
- `@pytest.mark.database` - Tests requiring database connection
- `@pytest.mark.auth` - Authentication-related tests
- `@pytest.mark.interview` - Interview functionality tests
- `@pytest.mark.profile` - User profile tests
- `@pytest.mark.slow` - Slow-running tests

## 🔧 Test Configuration

### pytest.ini

Key configurations:
- Test discovery patterns
- Coverage settings
- Output formatting
- Marker definitions

### conftest.py

Shared fixtures:
- `client` - FastAPI test client
- `test_db` - Test database setup/teardown
- `test_user` - Sample user data
- `mock_app_globals` - Mocked application state
- `sample_interview_session` - Sample interview data

### .env.test

Test environment variables:
- Database connection string
- Secret keys (test only)
- Feature flags
- Configuration overrides

## 📈 Coverage Goals

| Component | Target Coverage |
|-----------|----------------|
| Database Layer | 95%+ |
| Authentication | 90%+ |
| Interview Logic | 90%+ |
| Profile Management | 85%+ |
| API Endpoints | 85%+ |
| **Overall** | **90%+** |

## 🧪 Test Types

### 1. Unit Tests
- Test individual functions in isolation
- Mock external dependencies
- Fast execution
- No database required

### 2. Integration Tests
- Test multiple components together
- Use test database
- Test API endpoints
- Verify end-to-end flows

### 3. Database Tests
- Test CRUD operations
- Verify data integrity
- Test transactions and rollbacks
- Validate constraints

## 🐛 Debugging Tests

### Run with Print Statements
```bash
pytest -s tests/test_database.py
```

### Run with PDB Debugger
```bash
pytest --pdb tests/test_auth.py
```

### Show Detailed Failure Info
```bash
pytest -vv --tb=long
```

### Run Last Failed Tests Only
```bash
pytest --lf
```

## 📝 Writing New Tests

### Test Structure
```python
import pytest
from conftest import assert_success_response

@pytest.mark.integration
class TestMyFeature:
    """Test my new feature."""

    def test_feature_success(self, client, test_db):
        """Test successful feature execution."""
        response = client.post("/my-endpoint", json={"data": "value"})
        
        data = assert_success_response(response, 200)
        assert data["result"] == "expected"

    def test_feature_validation_error(self, client):
        """Test feature validation."""
        response = client.post("/my-endpoint", json={})
        assert response.status_code == 422
```

### Best Practices

1. **One assertion per test** (when possible)
2. **Descriptive test names** (test_what_when_expected)
3. **Use fixtures** for setup/teardown
4. **Mock external services** in unit tests
5. **Clean up after tests** (database, files, etc.)
6. **Test edge cases** and error conditions
7. **Keep tests independent** (no order dependency)

## 🔄 Continuous Integration

### GitHub Actions Example
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test_password
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          cd backend
          pytest --cov --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)

## 🆘 Troubleshooting

### Database Connection Error
```bash
# Check if PostgreSQL is running
pg_isready

# Verify DATABASE_URL in .env.test
echo $DATABASE_URL
```

### Import Errors
```bash
# Install in development mode
pip install -e .

# Or add to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Fixture Not Found
- Check that conftest.py is in tests/ directory
- Verify fixture is properly defined with @pytest.fixture
- Check fixture scope (function, class, module, session)

## 📊 Viewing Coverage Reports

```bash
# Generate HTML coverage report
pytest --cov --cov-report=html

# Open in browser (Linux/Mac)
open htmlcov/index.html

# Open in browser (Windows)
start htmlcov/index.html
```

## 🎯 Next Steps

1. Run the full test suite: `pytest`
2. Check coverage: `pytest --cov`
3. Fix any failing tests
4. Add tests for new features
5. Maintain 90%+ coverage

---

**Note**: Some tests marked with `@pytest.mark.database` require a PostgreSQL database. Unit tests can run without a database by using mocks.
