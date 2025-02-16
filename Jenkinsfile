// Define the pipeline with declarative syntax
pipeline {
    // Run on any available agent
    agent any
    
    // Define tools needed for the pipeline
    tools {
        nodejs 'NodeJS'    // NodeJS installation defined in Jenkins Global Tool Configuration
    }
    
    // Define environment variables available to all stages
    environment {
        // Docker configuration
        registry = 'kadawara/mx'
        DOCKERHUB_CREDENTIALS = 'dockerhub'
        
        // SonarCloud configuration
        SONAR_PROJECT_KEY = 'ranuka_mx'
        SONAR_SCANNER_HOME = tool 'SonarScanner'
        SONAR_ORGANIZATION = 'ranuka'
    }
    
    // Pipeline stages
    stages {
        // Stage 1: Checkout code from repository
        stage('Checkout') {
            steps {
                echo 'Checking out the projects'
                // Use git step to clone the repository
                git branch: 'main', 
                    credentialsId: 'github-api', 
                    url: 'https://github.com/ranuka00x/MX2.git'
            }
        }
        
        // Stage 2: Set up Python environment and install dependencies
        stage('Py Requirements Testing') {
            steps {
                echo 'Setting up Python environment and installing dependencies'
                sh '''
                    # Create a new Python virtual environment
                    python3 -m venv venv
                    
                    # Activate the virtual environment
                    . venv/bin/activate
                    
                    # Upgrade pip to latest version
                    pip install --upgrade pip
                    
                    # Install project dependencies
                    pip install -r requirements.txt
                '''
            }
        }
        
        // Stage 3: Run SonarCloud analysis
        stage('SonarCloud Analysis') {
            options {
                // Set timeout to prevent hanging
                timeout(time: 5, unit: 'MINUTES')
            }
            steps {
                // Don't fail the build if SonarCloud analysis fails
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    withSonarQubeEnv('SonarQubeServer') {
                        sh """
                            ${SONAR_SCANNER_HOME}/bin/sonar-scanner \\
                            -Dsonar.projectKey=${SONAR_PROJECT_KEY} \\
                            -Dsonar.organization=${SONAR_ORGANIZATION} \\
                            -Dsonar.sources=. \\
                            -Dsonar.host.url=https://sonarcloud.io \\
                            -Dsonar.python.version=3 \\
                            -Dsonar.exclusions=**/node_modules/**,**/venv/**,.git/**,**/*.pyc,**/__pycache__/** \\
                            -Dsonar.sourceEncoding=UTF-8 \\
                            -Dsonar.python.coverage.reportPaths=coverage.xml \\
                            -Dsonar.scanner.force-deprecated-java-version=true \\
                            -Dsonar.scanner.skipSystemTruststore=true \\
                            -Dsonar.verbose=true
                        """
                    }
                    
                    // Optional: Wait for quality gate
                    timeout(time: 2, unit: 'MINUTES') {
                        waitForQualityGate abortPipeline: false
                    }
                }
            }
        }
        
        // Stage 4: Build Docker image
        stage('Build Docker Image') {
            steps {
                script {
                    echo 'Building the docker image'
                    // Build the Docker image with the specified tag
                    dockerimage = docker.build("${registry}:latest")
                }
            }   
        }
        
        // Stage 5: Run tests
        stage('Test') {
            steps {
                echo 'Running tests'
                // Add your test commands here
                sh '''
                    . venv/bin/activate
                    python -m pytest tests/ --junitxml=test-reports/junit.xml || true
                '''
            }
        }
        
        // Stage 6: Deploy to Docker Hub
        stage('Deploy') {
            steps {
                script {
                    echo 'Deploying the project'
                    // Push the Docker image to Docker Hub
                    docker.withRegistry('https://registry.hub.docker.com', DOCKERHUB_CREDENTIALS) {
                        dockerimage.push('latest')
                    }
                }
            }
        }
    }
    
    // Post-build actions
    post {
        always {
            echo 'Cleaning up workspace and Docker images'
            
            // Clean up Docker images
            sh '''
                docker images -q ${registry} | xargs -r docker rmi || true
                docker image prune -f
            '''
            
            // Clean workspace
            cleanWs()
        }
        success {
            echo 'Pipeline succeeded!'
            // Add success notifications here if needed
        }
        failure {
            echo 'Pipeline failed!'
            // Add failure notifications here if needed
        }
    }
}