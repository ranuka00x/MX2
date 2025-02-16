pipeline {
    agent any
    
    tools {
        nodejs 'NodeJS'
    }
    
    environment {
        registry = 'kadawara/mx'
        DOCKERHUB_CREDENTIALS = 'dockerhub'
        SONAR_PROJECT_KEY = 'ranuka_mx'
        SONAR_SCANNER_HOME = tool 'SonarScanner'
        SONAR_ORGANIZATION = 'ranuka'

        BUILD_VERSION = "${BUILD_NUMBER}"
        TIMESTAMP = sh(script: 'date +%Y%m%d_%H%M%S', returnStdout: true).trim()

    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out the projects'
                git branch: 'main', 
                    credentialsId: 'github-api', 
                    url: 'https://github.com/ranuka00x/MX2.git'
            }
        }
        
        stage('Py Requirements Testing') {
            steps {
                echo 'Setting up Python environment and installing dependencies...'
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }
        
        stage('SonarCloud Analysis') {
            options {
                timeout(time: 5, unit: 'MINUTES')
            }
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    withSonarQubeEnv('SonarQubeServer') {
                        sh """
                            ${SONAR_SCANNER_HOME}/bin/sonar-scanner \\
                            -Dsonar.projectKey=${SONAR_PROJECT_KEY} \\
                            -Dsonar.organization=${SONAR_ORGANIZATION} \\
                            -Dsonar.sources=. \\
                            -Dsonar.host.url=https://sonarcloud.io \\
                            -Dsonar.python.version=3 \\
                            -Dsonar.inclusions=**/*.py,**/*.html,**/*.css \\
                            -Dsonar.exclusions=**/venv/**,.git/**,**/*.pyc,**/__pycache__/** \\
                            -Dsonar.sourceEncoding=UTF-8 \\
                            -Dsonar.scanner.force-deprecated-java-version=true \\
                            -Dsonar.scanner.skipSystemTruststore=true
                        """
                    }
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    echo 'Building the docker image.'
                    dockerimage = docker.build("${registry}:${BUILD_VERSION}")



                }
            }   
        }
        
        stage('Deploy') {
            steps {
                script {
                    echo 'Deploying the project'
                    docker.withRegistry('https://registry.hub.docker.com', DOCKERHUB_CREDENTIALS) {
                        dockerimage.push()

                        sh """
                            echo "${BUILD_NUMBER}" > .deployed-version
                        """

                    }
                }
            }
        }
    }
    
    post {
        always {
            echo 'Cleaning up workspace and Docker images'
            withCredentials([usernamePassword(credentialsId: DOCKERHUB_CREDENTIALS, passwordVariable: 'DOCKERHUB_PASSWORD', usernameVariable: 'DOCKERHUB_USERNAME')]) {
                sh '''
                    # Clean local images
                    docker images --format '{{.Repository}}:{{.Tag}}' | grep "${registry}" | xargs -r docker rmi -f || true
                    docker images --format '{{.Repository}}:{{.Tag}}' | grep "registry.hub.docker.com/${registry}" | xargs -r docker rmi -f || true
                    docker image prune -f
                    
                    # Get token for Docker Hub API
                    TOKEN=$(curl -s -H "Content-Type: application/json" -X POST -d "{\\\"username\\\": \\\"${DOCKERHUB_USERNAME}\\\", \\\"password\\\": \\\"${DOCKERHUB_PASSWORD}\\\"}" https://hub.docker.com/v2/users/login/ | jq -r .token)
                    
                    # Get all tags
                    TAGS=$(curl -s -H "Authorization: JWT ${TOKEN}" https://hub.docker.com/v2/repositories/${registry}/tags?page_size=100 | jq -r '.results[].name')
                    
                    # Sort tags numerically and keep only tags older than last 10
                    OLD_TAGS=$(echo "${TAGS}" | sort -nr | tail -n +11)
                    
                    # Delete old tags
                    for tag in ${OLD_TAGS}; do
                        curl -s -X DELETE -H "Authorization: JWT ${TOKEN}" https://hub.docker.com/v2/repositories/${registry}/tags/${tag}/
                        echo "Deleted tag: ${tag}"
                    done
                '''
                cleanWs()
            }
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}