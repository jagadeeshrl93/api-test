pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "jagadeesh916/api-test"
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t $DOCKER_IMAGE:latest .'
            }
        }

        stage('Test Docker Image') {
            steps {
                sh 'docker images | grep k8s-yaml-api'
            }
        }
    }
}