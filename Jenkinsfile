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
        DOCKER_IMAGE    = 'ai-voice-interview-backend'
        DOCKER_TAG      = "${env.BUILD_NUMBER}"
        DOCKER_REGISTRY = 'othmansalahi'
        PYTHON_VERSION  = '3.12'
        VENV_PATH       = "${WORKSPACE}/venv"
        DATABASE_URL    = credentials('test-database-url')
        SECRET_KEY      = credentials('test-secret-key')
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
        timeout(time: 60, unit: 'MINUTES')
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

        stage('Check Docker Access') {
            steps {
                script {
                    if (sh(script: 'docker info > /dev/null 2>&1', returnStatus: true) == 0) {
                        env.DOCKER_CMD       = 'docker'
                        env.DOCKER_AVAILABLE = 'true'
                        echo 'Docker accessible directly.'
                    } else if (sh(script: 'sudo docker info > /dev/null 2>&1', returnStatus: true) == 0) {
                        env.DOCKER_CMD       = 'sudo docker'
                        env.DOCKER_AVAILABLE = 'true'
                        echo 'Docker accessible via sudo.'
                    } else {
                        env.DOCKER_CMD = 'docker'
                        echo 'WARNING: could not verify docker access. Trying plain docker anyway.'
                    }
                }
            }
        }

        stage('Setup Python Environment') {
            steps {
                echo 'Setting up Python virtual environment...'
                dir('backend') {
                    sh '''
                        # Create venv
                        python${PYTHON_VERSION} -m venv ${VENV_PATH} --clear

                        # Use venv pip directly to avoid system pip restrictions
                        ${VENV_PATH}/bin/pip install --upgrade pip setuptools wheel --no-cache-dir

                        # Install CPU-only PyTorch to avoid huge CUDA downloads
                        ${VENV_PATH}/bin/pip install --no-cache-dir \
                            --index-url https://download.pytorch.org/whl/cpu \
                            --extra-index-url https://pypi.org/simple \
                            torch==2.2.0 torchvision==0.17.0

                        # Install all project requirements
                        ${VENV_PATH}/bin/pip install --no-cache-dir -r requirements.txt
                    '''
                }
            }
        }

        stage('Setup Frontend Environment') {
            steps {
                echo 'Installing frontend dependencies...'
                dir('frontend') {
                    sh 'npm ci'
                }
            }
        }

        stage('Lint & Code Quality') {
            steps {
                echo 'Running linters and code quality checks...'
                dir('backend') {
                    sh '''
                        ${VENV_PATH}/bin/pip install flake8 black --no-cache-dir

                        # Syntax and critical errors only
                        ${VENV_PATH}/bin/flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || true

                        # Code formatting check
                        ${VENV_PATH}/bin/black --check . || true
                    '''
                }
            }
        }

        stage('Run Frontend Tests') {
            steps {
                echo 'Running frontend tests...'
                dir('frontend') {
                    sh 'npm run test || true'
                }
            }
        }

        stage('Build Frontend') {
            steps {
                echo 'Building frontend application...'
                dir('frontend') {
                    sh 'npm run build'
                }
            }
        }

        stage('Run Backend Tests') {
            steps {
                echo 'Running backend test suite...'
                dir('backend') {
                    sh '''
                        ${VENV_PATH}/bin/pytest -v -m "not database" \
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
                    junit 'backend/test-results.xml'
                    publishHTML(target: [
                        allowMissing: true,
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
                        ${VENV_PATH}/bin/pip install safety --no-cache-dir
                        ${VENV_PATH}/bin/safety check --json || true
                    '''
                }
            }
        }

        stage('Cleanup Docker Resources') {
            steps {
                echo 'Cleaning up Docker resources...'
                sh '''
                    ${DOCKER_CMD} system prune -af --volumes || true
                    ${DOCKER_CMD} builder prune -af || true

                    # Keep only last 3 images of this project
                    IMAGES_TO_DELETE=$(($(${DOCKER_CMD} images ${DOCKER_IMAGE} -q | wc -l) - 3))
                    if [ $IMAGES_TO_DELETE -gt 0 ]; then
                        ${DOCKER_CMD} images ${DOCKER_IMAGE} -q | tail -n $IMAGES_TO_DELETE | xargs -r ${DOCKER_CMD} rmi -f || true
                    fi

                    df -h || true
                    ${DOCKER_CMD} system df || true
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                dir('backend') {
                    sh '''
                        ${DOCKER_CMD} build --no-cache -t ${DOCKER_IMAGE}:${DOCKER_TAG} .
                        ${DOCKER_CMD} tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest
                        ${DOCKER_CMD} tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:${GIT_COMMIT_HASH}
                    '''
                }
            }
        }

        stage('Test Docker Image') {
            steps {
                echo 'Testing Docker image...'
                script {
                    sh """
                        # Start postgres if not running
                        ${DOCKER_CMD} network create interview-network 2>/dev/null || true

                        ${DOCKER_CMD} run -d --name test-postgres-${BUILD_NUMBER} \
                            --network interview-network \
                            -e POSTGRES_USER=interview_user \
                            -e POSTGRES_PASSWORD=interview_password \
                            -e POSTGRES_DB=interview_db \
                            postgres:15

                        # Wait for postgres to be ready
                        sleep 10

                        # Run backend container
                        ${DOCKER_CMD} run -d --name test-container-${BUILD_NUMBER} \
                            --network interview-network \
                            -p 8001:8000 \
                            -e DATABASE_URL=postgresql://interview_user:interview_password@test-postgres-${BUILD_NUMBER}:5432/interview_db \
                            -e SECRET_KEY=\${SECRET_KEY} \
                            ${DOCKER_IMAGE}:${DOCKER_TAG}

                        # Wait for app to start and model to load
                        sleep 30

                        # Test health endpoint
                        curl -f http://localhost:8001/health || exit 1
                    """
                }
            }
            post {
                always {
                    sh """
                        ${DOCKER_CMD} stop test-container-${BUILD_NUMBER} 2>/dev/null || true
                        ${DOCKER_CMD} rm test-container-${BUILD_NUMBER} 2>/dev/null || true
                        ${DOCKER_CMD} stop test-postgres-${BUILD_NUMBER} 2>/dev/null || true
                        ${DOCKER_CMD} rm test-postgres-${BUILD_NUMBER} 2>/dev/null || true
                    """
                }
            }
        }

        stage('Push Docker Image') {
            when {
                allOf {
                    branch 'main'
                    expression { env.DOCKER_REGISTRY?.trim() }
                }
            }
            steps {
                echo 'Pushing Docker image to registry...'
                withCredentials([usernamePassword(credentialsId: 'docker-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh '''
                        echo "$DOCKER_PASS" | ${DOCKER_CMD} login -u "$DOCKER_USER" --password-stdin

                        ${DOCKER_CMD} tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG}
                        ${DOCKER_CMD} tag ${DOCKER_IMAGE}:latest ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:latest
                        ${DOCKER_CMD} tag ${DOCKER_IMAGE}:${GIT_COMMIT_HASH} ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${GIT_COMMIT_HASH}

                        ${DOCKER_CMD} push ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG}
                        ${DOCKER_CMD} push ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:latest
                        ${DOCKER_CMD} push ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${GIT_COMMIT_HASH}

                        ${DOCKER_CMD} logout
                    '''
                }
            }
        }

        stage('Deploy to Staging') {
            when { branch 'develop' }
            steps {
                echo 'Deploying to staging environment...'
                sh 'echo "Add staging deployment commands here"'
            }
        }

        stage('Deploy to Production') {
            when { branch 'main' }
            steps {
                echo 'Deploying to production environment...'
                input message: 'Deploy to Production?', ok: 'Deploy'
                sh 'echo "Add production deployment commands here"'
            }
        }
    }

    post {
        always {
            echo 'Cleaning up workspace...'
            cleanWs()
        }
        success {
            echo 'Pipeline completed successfully! ✅'
        }
        failure {
            echo 'Pipeline failed! ❌'
        }
    }
}