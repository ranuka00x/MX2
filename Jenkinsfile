pipeline{   
    agent any
    tools{
        nodejs 'NodeJS'
        }
    environment{
        registry = 'kadawara/mx'
        registryCredential = 'dockerhub'
        }
    stages{
        stage('Checkout'){
            steps{
                echo 'Checking out the projects'
                git branch: 'main', credentialsId: 'github-api', url: 'https://github.com/ranuka00x/MX2.git'
            }
        }
        stage('Requirements Testing'){
            steps{
                echo 'Building the project'
                sh 'python3 -m venv venv'
                sh '. venv/bin/activate'
                sh './venv/bin/pip install -r requirements.txt'
 
            }
        }
        stage('Build Docker Image'){
            steps{
                script{
                echo 'Building the docker image'
                docker.build('${registry}:latest)')
                }
            }   
            
        }
        stage('Deploy'){
            steps{
                echo 'Deploying the project'
            }
        }
    }
}