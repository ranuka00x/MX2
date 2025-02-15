pipeline {   
    agent any
    tools {
        nodejs 'NodeJS'
    }
    environment {
        registry = 'kadawara/mx'
        DOCKERHUB_CREDENTIALS = 'dockerhub'
        SONAR_PROJECT_KEY = 'mx'
        SONAR_SCANNER_HOME = tool 'SonarQubeScanner'
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

        stage('SonarQube Analysis') {
            steps {
                timeout(time: 15, unit: 'MINUTES') {
                    script {
                        try {
                            withCredentials([string(credentialsId: 'complete-cicd-02-token', variable: 'SONAR_TOKEN')]) {
                                withSonarQubeEnv('SonarQube') {
                                    sh """
                                        ${SONAR_SCANNER_HOME}/bin/sonar-scanner \
                                        -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                                        -Dsonar.sources=. \
                                        -Dsonar.host.url=http://20.119.81.146:9000 \
                                        -Dsonar.token=${SONAR_TOKEN} \
                                        -Dsonar.sourceEncoding=UTF-8 \
                                        -Dsonar.python.version=3 \
                                        -Dsonar.exclusions=venv/**
                                    """
                                }
                            }
                            // Wait for quality gate
                            timeout(time: 5, unit: 'MINUTES') {
                                def qg = waitForQualityGate()
                                if (qg.status != 'OK') {
                                    error "Quality gate failed: ${qg.status}"
                                }
                            }
                        } catch (Exception e) {
                            error "SonarQube analysis failed: ${e.message}"
                        }
                    }
                }
            }
        }
   
//        stage('SonarQube Analysis') {
//            def scannerHome = tool 'mysonar';
//            withSonarQubeEnv() {
//            sh "${scannerHome}/bin/sonar-scanner"
//            }
//        }

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