pipeline {
    agent any

    parameters {
        choice(
            name: 'DEPLOYMENT_STRATEGY',
            choices: ['blue-green', 'canary', 'shadow', 'ab', 'rolling'],
            description: 'Select the deployment strategy to use.'
        )
    }

    environment {
        PATH = "/opt/homebrew/bin:/usr/local/bin:${env.PATH}"
        DISPLAY = ":99"
        IMAGE_NAME = "aceest-app"
        NEW_VERSION = "green"
        OLD_VERSION = "blue"
        CANARY_REPLICAS = 1
        AB_TEST_LABEL = "ab-group"
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/2024tm93728-neeraj/aceest-fitness.git',
                    credentialsId: '07f00e0a-d651-488b-87ba-222b536f2562'
            }
        }

        stage('Setup Python') {
            steps {
                sh '''
                python3 -m venv venv
                . venv/bin/activate
                pip install --upgrade pip
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                . venv/bin/activate
                pip install -r requirements.txt
                pip install flake8 mypy pytest coverage types-fpdf2
                # Install yq for YAML editing
                if ! command -v yq >/dev/null 2>&1; then
                  brew install yq || sudo apt-get install -y yq || pip install yq
                fi
                '''
            }
        }

        stage('Lint') {
            steps {
                sh '''
                . venv/bin/activate
                flake8 . --exclude=venv,__pycache__,.git \
                    --count --select=E9,F63,F7,F82 --show-source --statistics

                flake8 . --exclude=venv,__pycache__,.git \
                    --count --exit-zero --max-complexity=10 --max-line-length=120 --statistics
                '''
            }
        }

        stage('Type Check') {
            steps {
                sh '''
                . venv/bin/activate
                mypy .
                '''
            }
        }

        stage('Test with Coverage') {
            steps {
                sh '''
                . venv/bin/activate
                coverage run -m pytest --maxfail=1 --disable-warnings -q
                coverage report -m
                coverage xml
                coverage report --fail-under=80
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('sonarQube') {
                    sh '''
                    . venv/bin/activate
                    sonar-scanner \
                      -Dsonar.projectKey=aceest-fitness \
                      -Dsonar.projectName="Aceest Fitness" \
                      -Dsonar.sources=. \
                      -Dsonar.exclusions=venv/** \
                      -Dsonar.python.coverage.reportPaths=coverage.xml
                    '''
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                eval $(minikube docker-env)
                docker build -t ${IMAGE_NAME}:${NEW_VERSION} .
                '''
            }
        }

        stage('Blue-Green Deployment') {
            when { expression { env.DEPLOYMENT_STRATEGY == 'blue-green' } }
            steps {
                sh '''
                sed 's/name: aceest-app/name: aceest-app-green/; s/version: blue/version: ${NEW_VERSION}/' k8s/deployment.yaml > k8s/deployment-green.yaml
                kubectl apply -f k8s/deployment-green.yaml
                '''
                sh '''
                kubectl rollout status deployment aceest-app-${NEW_VERSION} || exit 1
                kubectl patch service aceest-service -p '{"spec":{"selector":{"app":"aceest-app","version":"'${NEW_VERSION}'"}}}'
                '''
            }
        }

        stage('Canary Release') {
            when { expression { env.DEPLOYMENT_STRATEGY == 'canary' } }
            steps {
                sh """
                sed 's/name: aceest-app/name: aceest-app-canary/; s/version: blue/version: canary/' k8s/deployment.yaml > k8s/deployment-canary.yaml
                yq e '.spec.replicas = ${CANARY_REPLICAS}' -i k8s/deployment-canary.yaml
                kubectl apply -f k8s/deployment-canary.yaml
                """
                sh '''
                kubectl rollout status deployment aceest-app-canary || exit 1
                '''
            }
        }

        stage('Shadow Deployment') {
            when { expression { env.DEPLOYMENT_STRATEGY == 'shadow' } }
            steps {
                sh '''
                sed 's/name: aceest-app/name: aceest-app-shadow/; s/version: blue/version: shadow/' k8s/deployment.yaml > k8s/deployment-shadow.yaml
                kubectl apply -f k8s/deployment-shadow.yaml
                '''
                echo 'Shadow deployment created. No traffic routed.'
            }
        }

        stage('A/B Testing') {
            when { expression { env.DEPLOYMENT_STRATEGY == 'ab' } }
            steps {
                sh '''
                sed 's/name: aceest-app/name: aceest-app-b/; s/version: blue/version: b/' k8s/deployment.yaml > k8s/deployment-b.yaml
                kubectl apply -f k8s/deployment-b.yaml
                '''
                sh """
                kubectl patch service aceest-service -p '{"spec":{"selector":{"app":"aceest-app","${AB_TEST_LABEL}":"b"}}}'
                """
            }
        }

        stage('Rolling Update') {
            when { expression { env.DEPLOYMENT_STRATEGY == 'rolling' } }
            steps {
                sh '''
                kubectl apply -f k8s/deployment.yaml
                kubectl rollout status deployment aceest-app || exit 1
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                kubectl get pods
                '''
            }
        }

        stage('Cleanup Old Version') {
            steps {
                sh '''
                kubectl delete deployment aceest-app-${OLD_VERSION} || true
                '''
            }
        }
    }

    post {
        success {
            echo "✅ Deployment successful (${env.DEPLOYMENT_STRATEGY} strategy)"
        }
        failure {
            echo "❌ Deployment failed — rolling back"
            script {
                if (env.DEPLOYMENT_STRATEGY == 'blue-green') {
                    sh '''kubectl patch service aceest-service -p '{"spec":{"selector":{"app":"aceest-app","version":"'${OLD_VERSION}'"}}}' '''
                } else if (env.DEPLOYMENT_STRATEGY == 'canary') {
                    sh '''kubectl delete deployment aceest-app-canary || true'''
                } else if (env.DEPLOYMENT_STRATEGY == 'shadow') {
                    sh '''kubectl delete deployment aceest-app-shadow || true'''
                } else if (env.DEPLOYMENT_STRATEGY == 'ab') {
                    sh """
                    kubectl patch service aceest-service -p '{"spec":{"selector":{"app":"aceest-app","${AB_TEST_LABEL}":"a"}}}'
                    """
                } else if (env.DEPLOYMENT_STRATEGY == 'rolling') {
                    sh '''kubectl rollout undo deployment aceest-app'''
                }
            }
        }
        always {
            archiveArtifacts artifacts: 'aceest-app.tar.gz', fingerprint: true
        }
    }
}