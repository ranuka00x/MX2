pipeline{   
    agent any
    stages{
        stage('Checkout'){
            steps{
                echo 'Checking out the project'
                git branch: 'main', credentialsId: 'github-api', url: 'https://github.com/ranuka00x/MX2.git'
            }
        }
        stage('Build'){
            steps{
                echo 'Building the projectd'
                
            }
        }
        stage('Test'){
            steps{
                echo 'Testing the project'
            }
        }
        stage('Deploy'){
            steps{
                echo 'Deploying the project'
            }
        }
    }
}