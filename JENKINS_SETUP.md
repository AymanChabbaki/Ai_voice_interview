# Jenkins Setup Guide

## 📋 Prerequisites

1. Jenkins installed and running
2. Required Jenkins plugins installed
3. Docker installed on Jenkins agent/server
4. Git repository connected

---

## 🔌 Required Jenkins Plugins

Install these plugins via **Jenkins → Manage Jenkins → Manage Plugins**:

- **Pipeline** (for pipeline support)
- **Git** (for SCM integration)
- **Docker Pipeline** (for Docker builds)
- **Credentials Binding Plugin** (for secure credentials)
- **JUnit Plugin** (for test reports)
- **HTML Publisher Plugin** (for coverage reports)
- **Warnings Next Generation Plugin** (optional, for code quality)

---

## 🔐 Configure Jenkins Credentials

### Step-by-Step Guide

#### 1. Access Credentials Page

Navigate to: **Jenkins → Manage Jenkins → Credentials → System → Global credentials (unrestricted)**

Or direct URL: `http://your-jenkins-url/credentials/store/system/domain/_/`

---

#### 2. Add Test Database URL

Click **"+ Add Credentials"**, then:

| Field | Value |
|-------|-------|
| **Kind** | Secret text |
| **Scope** | Global |
| **Secret** | `postgresql://test_user:test_password@localhost:5432/test_interview_db` |
| **ID** | `test-database-url` |
| **Description** | Test Database Connection URL |

Click **Create**

---

#### 3. Add Test Secret Key

Click **"+ Add Credentials"**, then:

| Field | Value |
|-------|-------|
| **Kind** | Secret text |
| **Scope** | Global |
| **Secret** | `test_secret_key_for_testing_only_do_not_use_in_production` |
| **ID** | `test-secret-key` |
| **Description** | JWT Secret Key for Tests |

Click **Create**

---

#### 4. Add Docker Registry Credentials (Optional)

Only needed if pushing to Docker Hub or private registry:

Click **"+ Add Credentials"**, then:

| Field | Value |
|-------|-------|
| **Kind** | Username with password |
| **Scope** | Global |
| **Username** | Your Docker Hub username |
| **Password** | Your Docker Hub password or access token |
| **ID** | `docker-credentials` |
| **Description** | Docker Registry Credentials |

Click **Create**

---

#### 5. Add Production Deployment Keys (Optional)

For SSH deployment to servers:

Click **"+ Add Credentials"**, then:

| Field | Value |
|-------|-------|
| **Kind** | SSH Username with private key |
| **Scope** | Global |
| **Username** | `deploy` |
| **Private Key** | Enter directly or from file |
| **ID** | `production-ssh-key` |
| **Description** | Production Server SSH Key |

Click **Create**

---

## 🛠️ Configure Pipeline Job

### Create New Pipeline

1. **Jenkins Dashboard → New Item**
2. Enter name: `AI-Voice-Interview-Backend`
3. Select: **Pipeline**
4. Click **OK**

### Configure Pipeline

#### General Settings

- ✅ **Discard old builds**: Keep last 10 builds
- ✅ **GitHub project** (if applicable): Enter your repo URL
- ✅ **This project is parameterized** (optional):
  - Add String Parameter: `DOCKER_REGISTRY` (default: empty)
  - Add String Parameter: `DEPLOY_ENV` (default: staging)

#### Build Triggers

- ✅ **GitHub hook trigger for GITScm polling** (if using GitHub webhooks)
- ✅ **Poll SCM**: `H/5 * * * *` (check for changes every 5 minutes)

#### Pipeline Definition

- **Definition**: Pipeline script from SCM
- **SCM**: Git
- **Repository URL**: Your Git repository URL
- **Credentials**: Add Git credentials if private repo
- **Branch**: `*/main` (or `*/develop` for staging)
- **Script Path**: `Jenkinsfile`

Click **Save**

---

## 🔄 Environment Variables in Jenkinsfile

The Jenkinsfile references credentials using this syntax:

```groovy
environment {
    DATABASE_URL = credentials('test-database-url')  // References credential ID
    SECRET_KEY = credentials('test-secret-key')
}
```

### How Jenkins Injects Credentials

When you use `credentials('credential-id')`:
- Jenkins loads the secret from its credential store
- Creates environment variable in the pipeline
- Masks the value in console logs (shows `****`)
- Automatically available to all pipeline steps

---

## 📝 Customizing the Pipeline

### Update Docker Registry

Edit `Jenkinsfile` line 8:

```groovy
DOCKER_REGISTRY = 'docker.io/yourusername'  // Your registry
```

Or leave empty for local builds only.

### Update Python Version

Edit line 11:

```groovy
PYTHON_VERSION = '3.11'  // Or 3.10, 3.12, etc.
```

### Add More Environment Variables

Add to the `environment` block:

```groovy
environment {
    DATABASE_URL = credentials('test-database-url')
    SECRET_KEY = credentials('test-secret-key')
    
    // Add your own:
    AWS_REGION = 'us-east-1'
    DEPLOY_TARGET = credentials('deploy-server-url')
}
```

---

## 🧪 Testing Jenkins Configuration

### 1. Verify Credentials

Create a test job to verify credentials are accessible:

```groovy
pipeline {
    agent any
    environment {
        TEST_DB = credentials('test-database-url')
    }
    stages {
        stage('Test') {
            steps {
                sh 'echo "Database URL is set: ${TEST_DB}"'
            }
        }
    }
}
```

Console output will show: `Database URL is set: ****` (masked)

### 2. Run Pipeline

1. Go to your pipeline job
2. Click **"Build Now"**
3. Check **Console Output** for progress
4. Verify each stage completes successfully

### 3. Check Reports

After build completes:
- **Test Results**: Click on build → Test Result
- **Coverage Report**: Click on build → Coverage Report
- **Console Output**: Click on build → Console Output

---

## 🚨 Troubleshooting

### Credential Not Found

**Error**: `groovy.lang.MissingPropertyException: No such property: credentials`

**Solution**: 
- Verify credential ID matches exactly
- Ensure Credentials Binding plugin is installed
- Check credential scope is "Global"

### Docker Permission Denied

**Error**: `Got permission denied while trying to connect to Docker daemon`

**Solution**:
```bash
# Add Jenkins user to docker group
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

### Python Module Not Found

**Error**: `ModuleNotFoundError: No module named 'pytest'`

**Solution**: Pipeline installs dependencies automatically. If issue persists:
- Check `requirements.txt` is in backend folder
- Verify Python version matches system version
- Clear workspace and rebuild

### Tests Failing

**Error**: Tests pass locally but fail in Jenkins

**Solution**:
- Check Jenkins has access to test database
- Verify environment variables are set correctly
- Check file permissions on Jenkins workspace
- Review Console Output for detailed errors

---

## 🔒 Security Best Practices

### 1. Use Separate Test Database

Never use production database for tests:
```
Production: postgresql://user:pass@prod.example.com:5432/prod_db
Test:       postgresql://test_user:test_pass@localhost:5432/test_db
```

### 2. Rotate Credentials Regularly

Update credentials every 90 days:
- Go to credential in Jenkins
- Click "Update"
- Enter new secret
- Save

### 3. Use Jenkins Credentials, Not .env Files

❌ **Don't** commit `.env` files with secrets
✅ **Do** use Jenkins credentials store

### 4. Limit Credential Scope

- Use "Global" only when needed across all jobs
- Use "System" for most credentials
- Use specific domains for restricted access

### 5. Use Folder-Level Credentials

For multiple projects:
- Create folders in Jenkins
- Add credentials at folder level
- Only accessible to jobs in that folder

---

## 📊 Pipeline Visualization

After setting up, your pipeline will show:

```
┌─────────────┐
│  Checkout   │ ← Pull latest code
└──────┬──────┘
       │
┌──────▼──────┐
│ Setup Python│ ← Create venv, install deps
└──────┬──────┘
       │
┌──────▼──────┐
│    Lint     │ ← flake8, black
└──────┬──────┘
       │
┌──────▼──────┐
│  Run Tests  │ ← pytest with coverage
└──────┬──────┘
       │
┌──────▼──────┐
│Security Scan│ ← safety check
└──────┬──────┘
       │
┌──────▼──────┐
│Build Docker │ ← docker build
└──────┬──────┘
       │
┌──────▼──────┐
│ Test Image  │ ← Health check
└──────┬──────┘
       │
┌──────▼──────┐
│Push Image   │ ← To registry (if main)
└──────┬──────┘
       │
┌──────▼──────┐
│   Deploy    │ ← To staging/prod
└─────────────┘
```

---

## 🎯 Quick Reference

### Required Credential IDs

| Credential ID | Type | Purpose |
|--------------|------|---------|
| `test-database-url` | Secret text | Test database connection |
| `test-secret-key` | Secret text | JWT signing key for tests |
| `docker-credentials` | Username/Password | Docker registry login |

### Jenkinsfile Variables

| Variable | Default | Customizable |
|----------|---------|--------------|
| `DOCKER_IMAGE` | ai-voice-interview-backend | Yes |
| `DOCKER_REGISTRY` | (empty) | Yes - set your registry |
| `PYTHON_VERSION` | 3.11 | Yes |

### Build Commands

```bash
# Trigger build manually
curl -X POST http://jenkins-url/job/AI-Voice-Interview-Backend/build

# Trigger with parameters
curl -X POST http://jenkins-url/job/AI-Voice-Interview-Backend/buildWithParameters?DEPLOY_ENV=staging
```

---

## 📚 Additional Resources

- [Jenkins Credentials Plugin](https://www.jenkins.io/doc/book/using/using-credentials/)
- [Pipeline Syntax](https://www.jenkins.io/doc/book/pipeline/syntax/)
- [Docker Pipeline Plugin](https://docs.cloudbees.com/docs/admin-resources/latest/plugins/docker-workflow)
- [Best Practices](https://www.jenkins.io/doc/book/pipeline/pipeline-best-practices/)

---

## ✅ Checklist

Before running your first build:

- [ ] Jenkins plugins installed
- [ ] `test-database-url` credential created
- [ ] `test-secret-key` credential created
- [ ] `docker-credentials` credential created (if pushing images)
- [ ] Pipeline job created and configured
- [ ] Git repository connected
- [ ] Docker installed on Jenkins server
- [ ] Python 3.11 available on Jenkins server
- [ ] Test database accessible from Jenkins
- [ ] Jenkinsfile in repository root
- [ ] First build triggered and passing

You're ready to go! 🚀
