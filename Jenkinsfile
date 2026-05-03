pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "jagadeesh916/api-test"
        CONTAINER_NAME = "api-test"
        EC2_HOST = "3.142.97.193"
        EC2_USER = "ubuntu"
    }

    stages {

        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Login to Docker Hub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: '30f42ef0-3180-44a3-ace5-da3071a9cb85',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                    echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                    '''
                }
            }
        }

        stage('Build and Push Docker Image for EC2') {
            steps {
                sh '''
                docker buildx create --use || true

                docker buildx build \
                  --platform linux/amd64 \
                  -t $DOCKER_IMAGE:latest \
                  --push .
                '''
            }
        }

        stage('Deploy to EC2') {
            steps {
                sshagent(['Ec2']) {
                    sh '''
                    ssh -o StrictHostKeyChecking=no $EC2_USER@$EC2_HOST "
                        docker pull $DOCKER_IMAGE:latest &&
                        docker stop $CONTAINER_NAME || true &&
                        docker rm $CONTAINER_NAME || true &&
                        docker run -d \
                          --name $CONTAINER_NAME \
                          -p 8000:8000 \
                          --restart always \
                          $DOCKER_IMAGE:latest
                    "
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully.'
        }

        failure {
            echo 'Pipeline failed. Check console output.'
        }
    }
}