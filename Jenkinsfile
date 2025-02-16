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
                    echo 'Building the docker image'
                    dockerimage = docker.build("${registry}:latest")
                }
            }   
        }
        
        stage('Deploy') {
            steps {
                script {
                    echo 'Deploying the project'
                    docker.withRegistry('https://registry.hub.docker.com', DOCKERHUB_CREDENTIALS) {
                        dockerimage.push('latest')
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo 'Cleaning up workspace and Docker images'
            sh '''
                docker images -q ${registry} | xargs -r docker rmi || true
                docker image prune -f
            '''
            cleanWs()
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}