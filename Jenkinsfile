pipeline{   
    agent any
    tools{
        nodejs 'NodeJS2'
        }
    stages{
        stage('Checkout'){
            steps{
                echo 'Checking out the projects'
                git branch: 'main', credentialsId: 'github-api', url: 'https://github.com/ranuka00x/MX2.git'
            }
        }
        stage('Build'){
            steps{
                echo 'Building the project'
                sh 'python3 -m venv venv'
                sh '. venv/bin/activate'
                sh './venv/bin/pip install -r requirements.txt'
 
            }
        }
        stage('Test'){
            steps{
                echo 'Testing the project'
                sh 'node --version'
                sh 'npm --version'
            }
        }
        stage('Deploy'){
            steps{
                echo 'Deploying the project'
            }
        }
    }
}