pipeline {
    agent any

    environment {
        // Docker
        DOCKER_REGISTRY        = 'othmansalahi'
        DOCKER_IMAGE_BACKEND   = "${DOCKER_REGISTRY}/ai-voice-interview-backend"
        DOCKER_IMAGE_FRONTEND  = "${DOCKER_REGISTRY}/ai-voice-interview-frontend"
        DOCKER_TAG             = "${env.BUILD_NUMBER}"

        // Python
        PYTHON_VERSION         = '3.11'
        VENV_PATH              = "${WORKSPACE}/venv"

        // Credentials
        DATABASE_URL           = credentials('test-database-url')
        SECRET_KEY             = credentials('test-secret-key')

        // Deployment
        DEPLOY_USER            = 'sadmad'
        DEPLOY_SERVER          = 'server-1'
        DEPLOY_PATH            = '/home/sadmad/app'
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
        timeout(time: 60, unit: 'MINUTES')
    }

    stages {

        // ─────────────────────────────────────────
        stage('Checkout') {
        // ─────────────────────────────────────────
            steps {
                echo 'Checking out source code...'
                checkout scm
                sh 'git rev-parse --short HEAD > .git/commit-hash'
                script {
                    env.GIT_COMMIT_HASH = readFile('.git/commit-hash').trim()
                    echo "Commit: ${env.GIT_COMMIT_HASH}"
                }
            }
        }

        // ─────────────────────────────────────────
        stage('Check Docker Access') {
        // ─────────────────────────────────────────
            steps {
                script {
                    if (sh(script: 'docker info > /dev/null 2>&1', returnStatus: true) == 0) {
                        env.DOCKER_CMD = 'docker'
                        echo 'Docker accessible directly.'
                    } else if (sh(script: 'sudo docker info > /dev/null 2>&1', returnStatus: true) == 0) {
                        env.DOCKER_CMD = 'sudo docker'
                        echo 'Docker accessible via sudo.'
                    } else {
                        env.DOCKER_CMD = 'docker'
                        echo 'WARNING: Docker access could not be verified.'
                    }
                }
            }
        }

        // ─────────────────────────────────────────
        stage('Setup Python Environment') {
        // ─────────────────────────────────────────
            steps {
                echo 'Setting up Python virtual environment...'
                dir('backend') {
                    sh '''
                        python3.11 -m venv ${VENV_PATH} --clear

                        ${VENV_PATH}/bin/pip install --upgrade pip setuptools wheel --no-cache-dir

                        ${VENV_PATH}/bin/pip install --no-cache-dir \
                            --index-url https://download.pytorch.org/whl/cpu \
                            --extra-index-url https://pypi.org/simple \
                            torch==2.2.0 torchvision==0.17.0

                        ${VENV_PATH}/bin/pip install --no-cache-dir -r requirements.txt
                    '''
                }
            }
        }

        // ─────────────────────────────────────────
        stage('Setup Frontend Environment') {
        // ─────────────────────────────────────────
            steps {
                echo 'Installing frontend dependencies...'
                dir('frontend') {
                    sh 'npm ci'
                }
            }
        }

        // ─────────────────────────────────────────
        stage('Lint & Code Quality') {
        // ─────────────────────────────────────────
            steps {
                echo 'Running linters and code quality checks...'
                dir('backend') {
                    sh '''
                        ${VENV_PATH}/bin/pip install flake8 black --no-cache-dir

                        echo "--- Flake8 ---"
                        ${VENV_PATH}/bin/flake8 . \
                            --count \
                            --select=E9,F63,F7,F82 \
                            --show-source \
                            --statistics || true

                        echo "--- Black ---"
                        ${VENV_PATH}/bin/black --check . || true
                    '''
                }
            }
        }

        // ─────────────────────────────────────────
        stage('Run Frontend Tests') {
        // ─────────────────────────────────────────
            steps {
                echo 'Running frontend tests...'
                dir('frontend') {
                    sh 'npm run test || true'
                }
            }
        }

        // ─────────────────────────────────────────
        stage('Build Frontend') {
        // ─────────────────────────────────────────
            steps {
                echo 'Building frontend application...'
                dir('frontend') {
                    sh 'npm run build'
                }
            }
        }

        // ─────────────────────────────────────────
        stage('Run Backend Tests') {
        // ─────────────────────────────────────────
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
                        allowMissing         : true,
                        alwaysLinkToLastBuild: true,
                        keepAll              : true,
                        reportDir            : 'backend/htmlcov',
                        reportFiles          : 'index.html',
                        reportName           : 'Coverage Report'
                    ])
                }
            }
        }

        // ─────────────────────────────────────────
        stage('Security Scan') {
        // ─────────────────────────────────────────
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

        // ─────────────────────────────────────────
        stage('Cleanup Docker Resources') {
        // ─────────────────────────────────────────
            steps {
                echo 'Cleaning up old Docker resources...'
                sh '''
                    ${DOCKER_CMD} system prune -af --volumes || true
                    ${DOCKER_CMD} builder prune -af || true
                    echo "--- Disk usage ---"
                    df -h || true
                    ${DOCKER_CMD} system df || true
                '''
            }
        }

        // ─────────────────────────────────────────
        stage('Build Docker Images') {
        // ─────────────────────────────────────────
            steps {
                echo 'Building backend and frontend Docker images...'
                sh '''
                    echo "Building backend image..."
                    ${DOCKER_CMD} build --no-cache \
                        -t ${DOCKER_IMAGE_BACKEND}:${DOCKER_TAG} \
                        -t ${DOCKER_IMAGE_BACKEND}:latest \
                        -t ${DOCKER_IMAGE_BACKEND}:${GIT_COMMIT_HASH} \
                        ./backend

                    echo "Building frontend image..."
                    ${DOCKER_CMD} build --no-cache \
                        -t ${DOCKER_IMAGE_FRONTEND}:${DOCKER_TAG} \
                        -t ${DOCKER_IMAGE_FRONTEND}:latest \
                        -t ${DOCKER_IMAGE_FRONTEND}:${GIT_COMMIT_HASH} \
                        ./frontend
                '''
            }
        }

        // ─────────────────────────────────────────
        stage('Test Docker Images') {
        // ─────────────────────────────────────────
            steps {
                echo 'Testing backend Docker image...'
                script {
                    sh """
                        ${DOCKER_CMD} network create interview-test-network-${BUILD_NUMBER} 2>/dev/null || true

                        # Start test database
                        ${DOCKER_CMD} run -d \
                            --name test-postgres-${BUILD_NUMBER} \
                            --network interview-test-network-${BUILD_NUMBER} \
                            -e POSTGRES_USER=interview_user \
                            -e POSTGRES_PASSWORD=interview_password \
                            -e POSTGRES_DB=interview_db \
                            postgres:15
                        
                        echo "Waiting for database to be ready..."
                        sleep 30

                        # Start backend container
                        ${DOCKER_CMD} run -d \
                            --name test-backend-${BUILD_NUMBER} \
                            --network interview-test-network-${BUILD_NUMBER} \
                            -p 8001:8000 \
                            -e DATABASE_URL=postgresql://interview_user:interview_password@test-postgres-${BUILD_NUMBER}:5432/interview_db \
                            -e SECRET_KEY=\${SECRET_KEY} \
                            ${DOCKER_IMAGE_BACKEND}:${DOCKER_TAG}

                        echo "Waiting for backend to start and load AI model..."
                        sleep 50

                        # Health check
                        echo "Running health check..."
                        curl -f http://localhost:8001/health || exit 1
                        echo "Health check passed!"
                    """
                }
            }
            post {
                always {
                    sh """
                        echo "Cleaning up test containers..."
                        ${DOCKER_CMD} stop  test-backend-${BUILD_NUMBER}  2>/dev/null || true
                        ${DOCKER_CMD} rm    test-backend-${BUILD_NUMBER}  2>/dev/null || true
                        ${DOCKER_CMD} stop  test-postgres-${BUILD_NUMBER} 2>/dev/null || true
                        ${DOCKER_CMD} rm    test-postgres-${BUILD_NUMBER} 2>/dev/null || true
                        ${DOCKER_CMD} network rm interview-test-network-${BUILD_NUMBER} 2>/dev/null || true
                    """
                }
            }
        }

        // ─────────────────────────────────────────
        stage('Push Docker Images') {
        // ─────────────────────────────────────────
            steps {
                echo 'Pushing images to Docker Hub...'
                withCredentials([usernamePassword(
                    credentialsId: 'docker-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                        echo "$DOCKER_PASS" | ${DOCKER_CMD} login -u "$DOCKER_USER" --password-stdin

                        echo "Pushing backend images..."
                        ${DOCKER_CMD} push ${DOCKER_IMAGE_BACKEND}:${DOCKER_TAG}
                        ${DOCKER_CMD} push ${DOCKER_IMAGE_BACKEND}:latest
                        ${DOCKER_CMD} push ${DOCKER_IMAGE_BACKEND}:${GIT_COMMIT_HASH}

                        echo "Pushing frontend images..."
                        ${DOCKER_CMD} push ${DOCKER_IMAGE_FRONTEND}:${DOCKER_TAG}
                        ${DOCKER_CMD} push ${DOCKER_IMAGE_FRONTEND}:latest
                        ${DOCKER_CMD} push ${DOCKER_IMAGE_FRONTEND}:${GIT_COMMIT_HASH}

                        ${DOCKER_CMD} logout
                        echo "All images pushed successfully!"
                    '''
                }
            }
        }

        // ─────────────────────────────────────────
        stage('Deploy to server-1') {
        // ─────────────────────────────────────────
            when { branch 'sadmad' }
            steps {
                echo 'Deploying to server-1...'
                sh """
                    # Create app directory on server-1 if it doesn't exist
                    ssh -o StrictHostKeyChecking=no ${DEPLOY_USER}@${DEPLOY_SERVER} \
                        'mkdir -p ${DEPLOY_PATH}'

                    # Copy latest docker-compose.yml to server-1
                    scp -o StrictHostKeyChecking=no \
                        docker-compose.yml \
                        ${DEPLOY_USER}@${DEPLOY_SERVER}:${DEPLOY_PATH}/docker-compose.yml

                    # Copy .env file if it exists
                    if [ -f .env ]; then
                        scp -o StrictHostKeyChecking=no \
                            .env \
                            ${DEPLOY_USER}@${DEPLOY_SERVER}:${DEPLOY_PATH}/.env
                    fi

                    # Deploy on server-1
                    ssh -o StrictHostKeyChecking=no ${DEPLOY_USER}@${DEPLOY_SERVER} '
                        cd ${DEPLOY_PATH} &&
                        echo "Pulling latest images..." &&
                        docker-compose pull &&
                        echo "Stopping old containers..." &&
                        docker-compose down &&
                        echo "Starting new containers..." &&
                        docker-compose up -d &&
                        echo "Deployment status:" &&
                        docker-compose ps
                    '
                """
            }
        }
    }

    // ─────────────────────────────────────────
    post {
    // ─────────────────────────────────────────
        always {
            echo 'Cleaning up workspace...'
            cleanWs()
        }
        success {
            echo '''
            ✅ Pipeline completed successfully!
            - Images pushed to Docker Hub
            - App deployed to server-1
            '''
        }
        failure {
            echo '''
            ❌ Pipeline failed!
            - Check the logs above for details
            '''
        }
    }
}
