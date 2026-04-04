pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Environment') {
            steps {
                sh '''
                python3 --version
                '''
            }
        }

        stage('Run Unit Tests') {
            steps {
                sh '''
                python3 -m unittest discover -s . -p "test_*.py" -v
                '''
            }
        }

        stage('Coverage Report') {
            steps {
                sh '''
                coverage run -m unittest discover -s . -p "test_*.py"
                coverage html
                '''
            }
        }
    }

    post {
        always {
            // Archive the HTML coverage report
            archiveArtifacts artifacts: 'htmlcov/**', fingerprint: true
        }
    }
}
