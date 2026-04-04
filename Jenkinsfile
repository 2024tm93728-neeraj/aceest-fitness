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
		export CI=true
                python3 -m unittest discover -s . -p "test_*.py" -v
                '''
            }
        }

        stage('Coverage Report') {
            steps {
                sh '''
		export CI=true
                coverage run -m unittest discover -s . -p "test_*.py"
                coverage html
                '''
            }
        }
    }

    post {
        always {
            // Archive the HTML coverage
            archiveArtifacts artifacts: 'htmlcov/**', fingerprint: true
        }
    }
}
