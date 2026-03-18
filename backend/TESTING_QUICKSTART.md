# Quick Start Guide - Backend Testing

## 🚀 5-Minute Setup

### 1. Install Dependencies (2 min)

```bash
cd backend
pip install -r requirements.txt
```

### 2. Run Tests (1 min)

#### On Linux/Mac:
```bash
# Quick tests (no database needed)
pytest -m unit

# All tests
pytest
```

#### On Windows PowerShell:
```powershell
# Quick tests
python -m pytest -m unit

# All tests
python -m pytest

# Or use the PowerShell script
.\run_tests.ps1 -Suite unit
```

### 3. View Results

```bash
# Generate coverage report
pytest --cov --cov-report=html

# Open report (Windows)
start htmlcov/index.html

# Open report (Linux/Mac)
open htmlcov/index.html
```

## 📊 Test Suite Overview

| Test File | Tests | Focus Area |
|-----------|-------|------------|
| test_database.py | 40+ | Database operations, user management |
| test_auth.py | 35+ | Registration, login, JWT tokens |
| test_interview.py | 45+ | Interview flow, scoring, sessions |
| test_profile.py | 40+ | Profiles, stats, history, analytics |
| test_general.py | 50+ | API endpoints, health, errors |

**Total: 200+ tests** covering all backend functionality

## 🎯 Common Test Commands

### Run Specific Test Suites

```bash
# Unit tests only (fast, no DB)
pytest -m unit

# Integration tests
pytest -m integration

# Database tests
pytest -m database

# Authentication tests
pytest tests/test_auth.py

# Interview tests
pytest tests/test_interview.py
```

### Run with Different Outputs

```bash
# Verbose output
pytest -v

# Very verbose (show full diffs)
pytest -vv

# Show print statements
pytest -s

# Run and stop at first failure
pytest -x
```

### Run Specific Tests

```bash
# Run by test name pattern
pytest -k "test_login"

# Run specific test class
pytest tests/test_auth.py::TestLogin

# Run specific test function
pytest tests/test_auth.py::TestLogin::test_login_success
```

### Coverage Reports

```bash
# Terminal coverage report
pytest --cov

# HTML coverage report
pytest --cov --cov-report=html

# XML coverage (for CI)
pytest --cov --cov-report=xml
```

## 🐛 Debugging Tests

```bash
# Run with debugger (stops on failure)
pytest --pdb

# Run with detailed traceback
pytest --tb=long

# Run last failed tests
pytest --lf

# Show test execution times
pytest --durations=10
```

## ⚡ Quick Test Scripts

### Using Python Script (All platforms)
```bash
# Run all tests
python run_tests.py

# Run unit tests
python run_tests.py unit

# Run with coverage
python run_tests.py coverage

# Run specific file
python run_tests.py -f test_auth.py

# Run with keyword
python run_tests.py -k "test_login"
```

### Using PowerShell Script (Windows)
```powershell
# Run all tests
.\run_tests.ps1

# Run unit tests
.\run_tests.ps1 -Suite unit

# Run with coverage
.\run_tests.ps1 -Suite coverage

# Run specific file
.\run_tests.ps1 -File test_auth.py

# Run with keyword
.\run_tests.ps1 -Keyword "login"
```

## 🔍 Test Markers Reference

| Marker | Description | Database Required? |
|--------|-------------|-------------------|
| `unit` | Fast unit tests | ❌ No |
| `integration` | Integration tests | ✅ Yes |
| `database` | Database-specific tests | ✅ Yes |
| `auth` | Authentication tests | ✅ Yes |
| `interview` | Interview functionality | ✅ Yes |
| `profile` | User profile tests | ✅ Yes |
| `slow` | Slow running tests | Varies |

Run tests by marker:
```bash
pytest -m unit         # Fast tests
pytest -m integration  # Integration tests
pytest -m "not slow"   # Exclude slow tests
```

## 📝 Test Database Setup (Optional)

For full integration tests, set up a test database:

### Using Docker (Recommended)
```bash
docker run -d --name test-postgres \
  -e POSTGRES_USER=test_user \
  -e POSTGRES_PASSWORD=test_password \
  -e POSTGRES_DB=test_interview_db \
  -p 5432:5432 \
  postgres:15
```

### Using Local PostgreSQL
```bash
# Create database
createdb test_interview_db

# Configure .env.test
echo "DATABASE_URL=postgresql://user:pass@localhost:5432/test_interview_db" > .env.test
```

### Without Database
Run only unit tests (no database needed):
```bash
pytest -m unit
```

## 📈 Interpreting Results

### Test Output Legend
- ✅ `.` = Passed
- ❌ `F` = Failed
- ⏭️ `s` = Skipped
- ⏭️ `x` = Expected to fail

### Coverage Report
- **Green**: Well tested (>90%)
- **Yellow**: Needs more tests (70-90%)
- **Red**: Poorly tested (<70%)

Target: **90%+ overall coverage**

## 🎓 Writing Your First Test

Create `tests/test_my_feature.py`:

```python
import pytest
from conftest import assert_success_response

@pytest.mark.integration
class TestMyFeature:
    """Test my new feature."""
    
    def test_feature_works(self, client):
        """Test that my feature returns success."""
        response = client.get("/my-endpoint")
        data = assert_success_response(response, 200)
        assert data["status"] == "success"
```

Run it:
```bash
pytest tests/test_my_feature.py -v
```

## 🆘 Common Issues

### Issue: "ModuleNotFoundError"
**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: "Database connection error"
**Solution**: Either set up test database OR run unit tests only
```bash
pytest -m unit  # Skip database tests
```

### Issue: "Fixture not found"
**Solution**: Make sure conftest.py is in tests/ directory

### Issue: "Tests are slow"
**Solution**: Run quick tests only
```bash
pytest -m "not slow"
```

## 🎉 Success!

If you see:
```
====== 200 passed in 15.23s ======
```

Congratulations! All tests are passing! 🎊

## 📚 Next Steps

1. ✅ Run `pytest` to verify everything works
2. ✅ Check coverage: `pytest --cov`
3. ✅ Read [tests/README.md](tests/README.md) for detailed docs
4. ✅ Write tests for new features
5. ✅ Keep coverage above 90%

---

**Need Help?** Check the main [tests/README.md](tests/README.md) for detailed information.
