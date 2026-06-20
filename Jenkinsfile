pipeline {
  agent any

  options {
    timeout(time: 20, unit: 'MINUTES')
    disableConcurrentBuilds()
    timestamps()
  }

  triggers {
    githubPush()
  }

  environment {
    DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')
    IMAGE_NAME = 'crazyfrog46/flask-calculator'
    IMAGE_TAG = "${env.BUILD_NUMBER}"
  }

  stages {

    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Setup Python & Install deps') {
      steps {
        sh '''
          set -e
          python3 -m venv .venv
          . .venv/bin/activate
          pip install --upgrade pip
          pip install -r requirements.txt
        '''
      }
    }

    stage('Run Tests') {
      steps {
        timeout(time: 5, unit: 'MINUTES') {
          sh '''
            set -e
            . .venv/bin/activate
            pytest --maxfail=1 --disable-warnings -q
          '''
        }
      }
    }

    stage('Build Docker Image') {
      steps {
        sh '''
          set -e
          docker build -t $IMAGE_NAME:$IMAGE_TAG .
          docker tag $IMAGE_NAME:$IMAGE_TAG $IMAGE_NAME:latest
        '''
      }
    }

    stage('Push to DockerHub') {
      steps {
        sh '''
          set -e
          echo "$DOCKERHUB_CREDENTIALS_PSW" | docker login -u "$DOCKERHUB_CREDENTIALS_USR" --password-stdin
          docker push $IMAGE_NAME:$IMAGE_TAG
          docker push $IMAGE_NAME:latest
        '''
      }
    }
  }

  post {
    always {
      echo 'Cleaning up workspace...'
      cleanWs(deleteDirs: true)
    }
    success {
      echo '✅ Build, test, and image push succeeded.'
    }
    failure {
      echo '❌ Pipeline failed.'
    }
  }
}