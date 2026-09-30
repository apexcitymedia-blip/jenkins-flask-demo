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
            if docker image inspect jenkins-demo:latest >/dev/null 2>&1; then
                docker tag jenkins-demo:latest jenkins-demo:previous
                echo "Previous image saved for rollback."
            fi

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
            sleep 10

            if curl -f http://localhost:5000/ >/dev/null 2>&1 && \
               [ "$(docker inspect --format='{{.State.Health.Status}}' jenkins-demo)" = "healthy" ]; then

                echo "Deployment successful."
                echo "Container health status: healthy"

            else

                echo "Deployment failed. Starting automatic rollback..."

                docker rm -f jenkins-demo || true

                docker run -d \
                    --name jenkins-demo \
                    -p 5000:5000 \
                    -e DATABASE_PATH=/data/barberbook.db \
                    -v barberbook-data:/data \
                    jenkins-demo:previous

                sleep 10

                curl -f http://localhost:5000/

                HEALTH=$(docker inspect --format='{{.State.Health.Status}}' jenkins-demo)

                echo "Rollback container health status: $HEALTH"

                test "$HEALTH" = "healthy"

                echo "Rollback completed successfully."
echo "The new deployment failed, so this Jenkins build will be marked FAILED."

exit 1

fi
        '''
    }
}
    }
}
