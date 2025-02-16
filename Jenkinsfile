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
                git branch: 'main', credentialsId: 'github-api', url: 'https://github.com/ranuka00x/MX2.git'
            }
        }
        stage('Py Requirements Testing') {
            steps {
                echo 'Building the project'
                sh 'python3 -m venv venv'
                sh '. venv/bin/activate'
                sh './venv/bin/pip install -r requirements.txt'
            }
        }
        stage('SonarCloud Analysis') {
            steps {
                withSonarQubeEnv('SonarQubeServer') {
                    sh """
                        sonar-scanner \\
                        -Dsonar.projectKey=${SONAR_PROJECT_KEY} \\
                        -Dsonar.organization=${SONAR_ORGANIZATION} \\
                        -Dsonar.sources=. \\
                        -Dsonar.host.url=https://sonarcloud.io
                    """
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

        stage('Test') {
            steps {
                echo 'Testing the project'
                
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
            // Clean up any images created during the build
            sh 'docker rmi $(docker images -q ${registry} || true) || true'
            // Remove any dangling images
            sh 'docker image prune -f'
            // Clean workspace
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