pipeline {
    agent any

    environment {
        DOCKER_IMAGE    = 'ai-voice-interview-backend'
        DOCKER_TAG      = "${env.BUILD_NUMBER}"
        DOCKER_REGISTRY = 'othmansalahi'
        PYTHON_VERSION  = '3.11'
        VENV_PATH       = "${WORKSPACE}/venv"
        DATABASE_URL    = credentials('test-database-url')
        SECRET_KEY      = credentials('test-secret-key')
        DEPLOY_SERVER   = 'server-1'
        DEPLOY_USER     = 'sadmad'
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
                        echo 'WARNING: could not verify docker access.'
                    }
                }
            }
        }

        stage('Setup Python Environment') {
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
                echo 'Running linters...'
                dir('backend') {
                    sh '''
                        ${VENV_PATH}/bin/pip install flake8 black --no-cache-dir
                        ${VENV_PATH}/bin/flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || true
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
                echo 'Building frontend...'
                dir('frontend') {
                    sh 'npm run build'
                }
            }
        }

        stage('Run Backend Tests') {
            steps {
                echo 'Running backend tests...'
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
                echo 'Running security scan...'
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
                sh '''
                    ${DOCKER_CMD} system prune -af --volumes || true
                    ${DOCKER_CMD} builder prune -af || true
                    df -h || true
                    ${DOCKER_CMD} system df || true
                '''
            }
        }

        stage('Build Docker Images') {
            steps {
                echo 'Building Docker images...'
                sh '''
                    ${DOCKER_CMD} build --no-cache \
                        -t ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG} \
                        -t ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:latest \
                        ./backend

                    ${DOCKER_CMD} build --no-cache \
                        -t ${DOCKER_REGISTRY}/ai-voice-interview-frontend:${DOCKER_TAG} \
                        -t ${DOCKER_REGISTRY}/ai-voice-interview-frontend:latest \
                        ./frontend
                '''
            }
        }

        stage('Test Docker Image') {
            steps {
                script {
                    sh """
                        ${DOCKER_CMD} network create interview-network 2>/dev/null || true

                        ${DOCKER_CMD} run -d --name test-postgres-${BUILD_NUMBER} \
                            --network interview-network \
                            -e POSTGRES_USER=interview_user \
                            -e POSTGRES_PASSWORD=interview_password \
                            -e POSTGRES_DB=interview_db \
                            postgres:15

                        sleep 30

                        ${DOCKER_CMD} run -d --name test-container-${BUILD_NUMBER} \
                            --network interview-network \
                            -p 8001:8000 \
                            -e DATABASE_URL=postgresql://interview_user:interview_password@test-postgres-${BUILD_NUMBER}:5432/interview_db \
                            -e SECRET_KEY=\${SECRET_KEY} \
                            ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG}

                        sleep 50
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
                        ${DOCKER_CMD} network rm interview-network 2>/dev/null || true
                    """
                }
            }
        }

        stage('Push Docker Images') {
            when {
                branch 'sadmad'
            }
            steps {
                echo 'Pushing images to Docker Hub...'
                withCredentials([usernamePassword(
                    credentialsId: 'docker-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                        echo "$DOCKER_PASS" | ${DOCKER_CMD} login -u "$DOCKER_USER" --password-stdin

                        ${DOCKER_CMD} push ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG}
                        ${DOCKER_CMD} push ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:latest

                        ${DOCKER_CMD} push ${DOCKER_REGISTRY}/ai-voice-interview-frontend:${DOCKER_TAG}
                        ${DOCKER_CMD} push ${DOCKER_REGISTRY}/ai-voice-interview-frontend:latest

                        ${DOCKER_CMD} logout
                    '''
                }
            }
        }

        stage('Deploy to server-1') {
            when {
                branch 'sadmad'
            }
            steps {
                echo 'Deploying to server-1 via SSH...'
                sh """
                    ssh -o StrictHostKeyChecking=no ${DEPLOY_USER}@${DEPLOY_SERVER} '
                        cd /home/sadmad/app &&
                        docker-compose pull &&
                        docker-compose down &&
                        docker-compose up -d &&
                        docker-compose ps
                    '
                """
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
