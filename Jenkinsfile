pipeline {
    agent any
    
    environment {
        // Docker
        DOCKER_IMAGE = 'ai-voice-interview-backend'
        DOCKER_TAG = "${env.BUILD_NUMBER}"
        DOCKER_REGISTRY = '' // Set your registry URL if using one (e.g., 'docker.io/username')
        
        // Python
        PYTHON_VERSION = '3.11'
        VENV_PATH = "${WORKSPACE}/venv"
        
        // Test environment
        DATABASE_URL = credentials('test-database-url') // Configure in Jenkins credentials
        SECRET_KEY = credentials('test-secret-key')
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
                        python${PYTHON_VERSION} -m venv ${VENV_PATH}
                        . ${VENV_PATH}/bin/activate
                        pip install --upgrade pip
                        pip install -r requirements.txt
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
