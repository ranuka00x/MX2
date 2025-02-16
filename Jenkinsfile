pipeline {
    agent any
    
    tools {
        nodejs 'NodeJS'
    }
    
    environment {
        // The registry variable holds your Docker Hub repository information
        registry = 'kadawara/mx'
        DOCKERHUB_CREDENTIALS = 'dockerhub'
        
        // SonarCloud configuration remains the same
        SONAR_PROJECT_KEY = 'ranuka_mx'
        SONAR_SCANNER_HOME = tool 'SonarScanner'
        SONAR_ORGANIZATION = 'ranuka'
        
        // We'll use Jenkins' built-in BUILD_NUMBER for versioning
        // BUILD_NUMBER is automatically provided by Jenkins
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
                echo 'Setting up Python environment and installing dependencies'
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
                    echo "Building Docker image with build number: ${BUILD_NUMBER}"
                    // Build the image with the build number as the tag
                    dockerimage = docker.build("${registry}:${BUILD_NUMBER}")
                }
            }   
        }
        
        stage('Deploy') {
            steps {
                script {
                    echo "Deploying version ${BUILD_NUMBER} to Docker Hub"
                    docker.withRegistry('https://registry.hub.docker.com', DOCKERHUB_CREDENTIALS) {
                        // Push the image with the build number tag
                        dockerimage.push()
                        
                        // Store the deployed version number for reference
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
            sh """
                # Remove the local image we just built and pushed
                docker rmi ${registry}:${BUILD_NUMBER} || true
                
                # Clean up any dangling images
                docker image prune -f
            """
            // Keep the .deployed-version file but clean everything else
            cleanWs(excludePatterns: ['.deployed-version'])
        }
        success {
            echo "Pipeline succeeded! Deployed version: ${BUILD_NUMBER}"
        }
        failure {
            echo "Pipeline failed during version: ${BUILD_NUMBER} deployment"
        }
    }
}