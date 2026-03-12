/*
 * AI Voice Interview Backend - Jenkins CI/CD Pipeline
 * 
 * SETUP REQUIRED:
 * 1. Install plugins: Docker Pipeline, Git, JUnit, HTML Publisher
 * 2. Add credentials in Jenkins (see JENKINS_SETUP.md):
 *    - ID: 'test-database-url' (Secret text)
 *    - ID: 'test-secret-key' (Secret text)  
 *    - ID: 'docker-credentials' (Username/Password) - for pushing images
 * 3. Customize variables below as needed
 */

pipeline {
    agent any
    
    environment {
        // ===================================================================
        // CUSTOMIZE THESE VARIABLES
        // ===================================================================
        
        // Docker Configuration
        DOCKER_IMAGE = 'ai-voice-interview-backend'  // Image name
        DOCKER_TAG = "${env.BUILD_NUMBER}"            // Tag with build number
        DOCKER_REGISTRY = 'othmansalahi'                          // e.g., 'docker.io/yourusername' or 'registry.example.com'
        
        // Python Configuration
        PYTHON_VERSION = '3.12'                       // Python version (3.10, 3.11, 3.12)
        VENV_PATH = "${WORKSPACE}/venv"               // Virtual environment path
        
        // ===================================================================
        // JENKINS CREDENTIALS (DO NOT MODIFY)
        // Configure these in: Jenkins → Credentials → Add Credentials
        // ===================================================================
        
        // Test Database URL - Add as "Secret text" with ID: test-database-url
        // Example: postgresql://test_user:test_password@localhost:5432/test_interview_db
        DATABASE_URL = credentials('test-database-url')
        
        // JWT Secret Key - Add as "Secret text" with ID: test-secret-key
        // Example: test_secret_key_for_testing_only
        SECRET_KEY = credentials('test-secret-key')
        
        // Docker Registry Credentials - Add as "Username with password" with ID: docker-credentials
        // Required only if DOCKER_REGISTRY is set and you want to push images
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code...'
                checkout scm
                sh 'git rev-parse --short HEAD > .git/commit-hash'
                script {
                    env.GIT_COMMIT_HASH = readFile('.git/commit-hash').trim()
                }
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                echo 'Setting up Python virtual environment...'
                dir('backend') {
                    sh '''
                        # 1. Create a local temp folder to avoid filling up /tmp
                        mkdir -p .pip_tmp
                        export TMPDIR="${WORKSPACE}/backend/.pip_tmp"

                        # 2. Setup venv
                        python${PYTHON_VERSION} -m venv ${VENV_PATH}
                        . ${VENV_PATH}/bin/activate

                                                # 3. Keep pip cache inside workspace and disable wheel caching to save disk
                                                export PIP_CACHE_DIR="${WORKSPACE}/backend/.pip_cache"
                                                export PIP_NO_CACHE_DIR=1
                                                mkdir -p "${PIP_CACHE_DIR}"

                                                # 4. Upgrade tools and fix the 'pkg_resources' issue for Pandas 2.0.3
                                                pip install --upgrade pip setuptools wheel --no-cache-dir

                                                # 5. Force CPU-only PyTorch wheels in CI to avoid huge CUDA downloads
                                                pip install --no-cache-dir \
                                                    --index-url https://download.pytorch.org/whl/cpu \
                                                    --extra-index-url https://pypi.org/simple \
                                                    torch==2.2.0 torchvision==0.17.0

                                                # 6. Install all project requirements (torch/vision are already satisfied)
                                                pip install --no-cache-dir -r requirements.txt

                                                # 7. Cleanup temp and cache folders
                        rm -rf .pip_tmp
                                                rm -rf .pip_cache
                    '''
                }
            }
        }
        
        stage('Lint & Code Quality') {
            steps {
                echo 'Running linters and code quality checks...'
                dir('backend') {
                    sh '''
                        . ${VENV_PATH}/bin/activate
                        # Install linting tools
                        pip install flake8 black pylint
                        
                        # Run flake8 (with relaxed settings)
                        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || true
                        
                        # Check code formatting with black
                        black --check . || true
                    '''
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                echo 'Running test suite...'
                dir('backend') {
                    sh '''
                        . ${VENV_PATH}/bin/activate
                        
                        # Run unit tests only (skip database tests in CI)
                        pytest -v -m "not database" \
                            --junit-xml=test-results.xml \
                            --cov=. \
                            --cov-report=xml \
                            --cov-report=html \
                            --cov-report=term
                    '''
                }
            }
            post {
                always {
                    // Publish test results
                    junit 'backend/test-results.xml'
                    
                    // Publish coverage report
                    publishHTML(target: [
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'backend/htmlcov',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])
                }
            }
        }
        
        stage('Security Scan') {
            steps {
                echo 'Running security vulnerability scan...'
                dir('backend') {
                    sh '''
                        . ${VENV_PATH}/bin/activate
                        
                        # Install safety for dependency scanning
                        pip install safety
                        
                        # Scan for known vulnerabilities
                        safety check --json || true
                    '''
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                dir('backend') {
                    script {
                        // Build Docker image
                        dockerImage = docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                        
                        // Tag as latest
                        dockerImage.tag('latest')
                        
                        // Tag with git commit hash
                        dockerImage.tag(env.GIT_COMMIT_HASH)
                    }
                }
            }
        }
        
        stage('Test Docker Image') {
            steps {
                echo 'Testing Docker image...'
                script {
                    // Run container for testing
                    sh """
                        docker run -d --name test-container-${BUILD_NUMBER} \
                            -p 8001:8000 \
                            -e DATABASE_URL=\${DATABASE_URL} \
                            -e SECRET_KEY=\${SECRET_KEY} \
                            ${DOCKER_IMAGE}:${DOCKER_TAG}
                        
                        # Wait for container to start
                        sleep 10
                        
                        # Test health endpoint
                        curl -f http://localhost:8001/health || exit 1
                        
                        # Cleanup
                        docker stop test-container-${BUILD_NUMBER}
                        docker rm test-container-${BUILD_NUMBER}
                    """
                }
            }
        }
        
        stage('Push Docker Image') {
            when {
                branch 'main'
            }
            steps {
                echo 'Pushing Docker image to registry...'
                script {
                    // This requires Docker registry credentials configured in Jenkins
                    docker.withRegistry("https://${DOCKER_REGISTRY}", 'docker-credentials') {
                        dockerImage.push("${DOCKER_TAG}")
                        dockerImage.push('latest')
                        dockerImage.push(env.GIT_COMMIT_HASH)
                    }
                }
            }
        }
        
        stage('Deploy to Staging') {
            when {
                branch 'develop'
            }
            steps {
                echo 'Deploying to staging environment...'
                // Add your deployment commands here
                // Example: SSH to server and update container
                sh '''
                    echo "Deployment commands would go here"
                    # ssh user@staging-server "docker pull ${DOCKER_IMAGE}:${DOCKER_TAG} && docker-compose up -d"
                '''
            }
        }
        
        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            steps {
                echo 'Deploying to production environment...'
                input message: 'Deploy to Production?', ok: 'Deploy'
                
                // Add your production deployment commands here
                sh '''
                    echo "Production deployment commands would go here"
                    # ssh user@production-server "docker pull ${DOCKER_IMAGE}:${DOCKER_TAG} && docker-compose up -d"
                '''
            }
        }
    }
    
    post {
        always {
            echo 'Cleaning up...'
            // Clean up workspace
            cleanWs()
        }
        
        success {
            echo 'Pipeline completed successfully! ✅'
            // Send notifications (Slack, email, etc.)
        }
        
        failure {
            echo 'Pipeline failed! ❌'
            // Send failure notifications
        }
    }
}
