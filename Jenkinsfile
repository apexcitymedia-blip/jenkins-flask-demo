pipeline {
    agent any

    stages {

        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    . venv/bin/activate
                    python --version
                    python -m pytest
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build -t jenkins-demo:latest .
                '''
            }
        }

        stage('Deploy') {
    steps {
        sh '''
            docker volume create barberbook-data
            docker rm -f jenkins-demo 2>/dev/null || true
            docker run -d \
                --name jenkins-demo \
                -p 5000:5000 \
                -e DATABASE_PATH=/data/barberbook.db \
                -v barberbook-data:/data \
                jenkins-demo:latest
        '''
    }
}

        stage('Verify Deployment') {
    steps {
        sh '''
            sleep 3

            curl -f http://localhost:5000/

            HEALTH=$(docker inspect --format='{{.State.Health.Status}}' jenkins-demo)

            echo "Container health status: $HEALTH"

            test "$HEALTH" = "healthy"
        '''
            }
    }
}
