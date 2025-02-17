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
        USE_GKE_GCLOUD_AUTH_PLUGIN = 'True'

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

        stage('install argocd') {
            steps {
                sh '''
                    curl -sSL -o /usr/local/bin/argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
                    chmod +x /usr/local/bin/argocd
                    argocd login 34.72.142.43 --username admin --password p@ssw0rdwac123 --insecure
                    argocd app sync testapp
                '''
            }
        }

        stage('Check Kubernetes connection') {
            steps {
                withKubeConfig([credentialsId: 'kubernetes-config',
                               serverUrl: 'https://35.232.162.143']) {
                    sh '''
                        # Verify the plugin is installed
                        which gke-gcloud-auth-plugin
                        
                        # Your deployment commands
                        kubectl get nodes
                        kubectl get pods
                    '''
                }
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

                    // Tag the same image as latest
                    sh "docker tag ${registry}:${BUILD_VERSION} ${registry}:latest"

                    // Verify the images created
                    sh "docker images | grep '${registry}'"
                }
            }   
        }

        
        stage('Docker image into registry') {
            steps {
                script {
                    echo 'Deploying the project'
                    docker.withRegistry('https://registry.hub.docker.com', DOCKERHUB_CREDENTIALS) {
                        // Push the version tag
                        dockerimage.push("${BUILD_VERSION}")
                        
                        // Push the latest tag explicitly
                        dockerimage.push("latest")

                        sh """
                            echo "${BUILD_NUMBER}" > .deployed-version
                            echo "${BUILD_NUMBER}" > build.txt
                        """
                    }
                }
            }
        }

        stage('Deploy to Production') {
            steps {
                sshagent(credentials: ['production-server-ssh-key']) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no ranuka@172.212.92.250 "
                            cd /home/ranuka/mx2 && \
                            docker-compose -f docker-compose-prod.yml down && \
                            git pull && \
                            docker-compose -f docker-compose-prod.yml up -d
                        "
                    '''
                }
            }
        }
    }
    
    post {
        always {
            echo 'Waiting 2 minutes before cleanup...'
            sh 'sleep 30' // 120 seconds = 2 minutes
            echo 'Starting cleanup of workspace and Docker images'
            withCredentials([usernamePassword(credentialsId: DOCKERHUB_CREDENTIALS, passwordVariable: 'DOCKERHUB_PASSWORD', usernameVariable: 'DOCKERHUB_USERNAME')]) {
                sh '''
                    # Clean local images after pushing
                    docker images --format '{{.Repository}}:{{.Tag}}' | grep "${registry}" | xargs -r docker rmi -f || true
                    docker images --format '{{.Repository}}:{{.Tag}}' | grep "registry.hub.docker.com/${registry}" | xargs -r docker rmi -f || true
                    docker image prune -f

                    # Docker login
                    TOKEN=$(curl -s -H "Content-Type: application/json" -X POST -d "{\\\"username\\\": \\\"${DOCKERHUB_USERNAME}\\\", \\\"password\\\": \\\"${DOCKERHUB_PASSWORD}\\\"}" https://hub.docker.com/v2/users/login/ | jq -r .token)

                    # Get all tags
                    TAGS=$(curl -s -H "Authorization: JWT ${TOKEN}" https://hub.docker.com/v2/repositories/${registry}/tags?page_size=100 | jq -r '.results[].name')

                    # Sort tags numerically and keep only tags older than last 10, excluding 'latest'
                    OLD_TAGS=$(echo "${TAGS}" | grep -v "^latest$" | sort -nr | tail -n +11)

                    # Delete old tags
                    for tag in ${OLD_TAGS}; do
                        curl -s -X DELETE -H "Authorization: JWT ${TOKEN}" https://hub.docker.com/v2/repositories/${registry}/tags/${tag}/
                        echo "Deleted tag: ${tag}"
                    done
                '''
                cleanWs()
            }
        }
    }

}