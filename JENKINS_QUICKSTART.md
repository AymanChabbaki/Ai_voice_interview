# Quick Start: Jenkins Credentials Setup

## 🚀 5-Minute Setup

### Step 1: Access Jenkins Credentials

1. Open Jenkins in browser: `http://your-jenkins-url:8080`
2. Click **"Manage Jenkins"** (left sidebar)
3. Click **"Credentials"**
4. Click **"System"** → **"Global credentials (unrestricted)"**
5. Click **"+ Add Credentials"** button (left sidebar)

---

### Step 2: Add Test Database URL

**Fill in the form:**

```
┌─────────────────────────────────────────────────────────┐
│ Kind:        [Secret text ▼]                            │
├─────────────────────────────────────────────────────────┤
│ Scope:       [Global ▼]                                 │
├─────────────────────────────────────────────────────────┤
│ Secret:      postgresql://test_user:test_password@      │
│              localhost:5432/test_interview_db           │
├─────────────────────────────────────────────────────────┤
│ ID:          test-database-url                          │
├─────────────────────────────────────────────────────────┤
│ Description: Test Database Connection URL              │
└─────────────────────────────────────────────────────────┘

                     [Create]
```

Click **Create**

✅ Credential ID: **`test-database-url`** is now available

---

### Step 3: Add Test Secret Key

Click **"+ Add Credentials"** again:

```
┌─────────────────────────────────────────────────────────┐
│ Kind:        [Secret text ▼]                            │
├─────────────────────────────────────────────────────────┤
│ Scope:       [Global ▼]                                 │
├─────────────────────────────────────────────────────────┤
│ Secret:      test_secret_key_for_testing_only          │
├─────────────────────────────────────────────────────────┤
│ ID:          test-secret-key                            │
├─────────────────────────────────────────────────────────┤
│ Description: JWT Secret Key for Tests                  │
└─────────────────────────────────────────────────────────┘

                     [Create]
```

Click **Create**

✅ Credential ID: **`test-secret-key`** is now available

---

### Step 4: Add Docker Credentials (Optional)

**Only if you want to push images to Docker Hub or private registry**

Click **"+ Add Credentials"** again:

```
┌─────────────────────────────────────────────────────────┐
│ Kind:        [Username with password ▼]                 │
├─────────────────────────────────────────────────────────┤
│ Scope:       [Global ▼]                                 │
├─────────────────────────────────────────────────────────┤
│ Username:    your-dockerhub-username                    │
├─────────────────────────────────────────────────────────┤
│ Password:    your-dockerhub-password                    │
├─────────────────────────────────────────────────────────┤
│ ID:          docker-credentials                         │
├─────────────────────────────────────────────────────────┤
│ Description: Docker Registry Credentials                │
└─────────────────────────────────────────────────────────┘

                     [Create]
```

Click **Create**

✅ Credential ID: **`docker-credentials`** is now available

---

### Step 5: Verify Credentials

You should now see all credentials listed:

```
Global credentials (unrestricted)
┌──────────────────────┬──────────────────────┬────────────────┐
│ ID                   │ Name                 │ Kind           │
├──────────────────────┼──────────────────────┼────────────────┤
│ test-database-url    │ Test Database...     │ Secret text    │
├──────────────────────┼──────────────────────┼────────────────┤
│ test-secret-key      │ JWT Secret Key...    │ Secret text    │
├──────────────────────┼──────────────────────┼────────────────┤
│ docker-credentials   │ Docker Registry...   │ Username/Pass  │
└──────────────────────┴──────────────────────┴────────────────┘
```

---

## ✅ All Done!

Your Jenkins credentials are configured. Now you can:

1. **Create Pipeline Job**
2. **Connect to Git Repository**
3. **Run Build**

See [JENKINS_SETUP.md](JENKINS_SETUP.md) for detailed pipeline configuration.

---

## 🔍 How Jenkinsfile Uses These Credentials

In your Jenkinsfile:

```groovy
environment {
    // Jenkins will inject these values automatically
    DATABASE_URL = credentials('test-database-url')  // ← Uses ID
    SECRET_KEY = credentials('test-secret-key')       // ← Uses ID
}
```

When the pipeline runs:
- Jenkins loads secrets from credential store
- Creates environment variables
- **Masks values in logs** (shows `****` instead of actual secret)
- Pipeline steps can use `$DATABASE_URL` and `$SECRET_KEY`

---

## 🧪 Test Your Setup

Create a simple test pipeline:

1. Jenkins → New Item → Pipeline
2. Name: "Test-Credentials"
3. Pipeline script:

```groovy
pipeline {
    agent any
    environment {
        DB_URL = credentials('test-database-url')
        SECRET = credentials('test-secret-key')
    }
    stages {
        stage('Test') {
            steps {
                echo "Testing credentials..."
                sh '''
                    echo "Database URL length: ${#DB_URL}"
                    echo "Secret key length: ${#SECRET}"
                    echo "✓ Credentials are accessible!"
                '''
            }
        }
    }
}
```

4. Click "Build Now"
5. Check Console Output - you should see masked values `****`

---

## 🆘 Troubleshooting

### "Credentials not found"
- **Check**: Credential ID matches exactly (case-sensitive)
- **Check**: Scope is set to "Global"
- **Fix**: Recreate credential with correct ID

### "Access Denied"
- **Check**: Jenkins user has permission to access credentials
- **Fix**: Go to Manage Jenkins → Configure Global Security → Enable "Authorize Project" plugin

### "Credentials Binding Plugin missing"
- **Fix**: Go to Manage Jenkins → Plugins → Available → Search "Credentials Binding" → Install

---

## 📱 Quick Reference Card

**Print or bookmark this:**

| What | Where | ID |
|------|-------|-----|
| Database URL | Jenkins → Credentials | `test-database-url` |
| Secret Key | Jenkins → Credentials | `test-secret-key` |
| Docker Login | Jenkins → Credentials | `docker-credentials` |

**Jenkinsfile syntax:**
```groovy
credentials('credential-id-here')
```

That's it! 🎉
