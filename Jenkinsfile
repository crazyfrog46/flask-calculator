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

  stages {

    stage('Checkout') {
      steps {
        checkout scm
        sh '''
          set -e
          echo "Git version:"
          git --version
        '''
      }
    }

    stage('Setup Python') {
      steps {
        sh '''
          set -e
          python3 -m venv .venv
          . .venv/bin/activate
          pip install --upgrade pip
          deactivate || true
        '''
      }
    }

    stage('Install deps & Test') {
      steps {
        timeout(time: 5, unit: 'MINUTES') {
          sh '''
            set -e
            . .venv/bin/activate
            pip install -r requirements.txt
            pip install pytest
            pytest --maxfail=1 --disable-warnings -q
            deactivate || true
          '''
        }
      }
    }

    stage('Package') {
      steps {
        sh '''
          set -e
          tar czf build.tgz --exclude .venv --exclude __pycache__ --exclude .git *
        '''
        archiveArtifacts artifacts: 'build.tgz', fingerprint: true
      }
    }

    stage('Deploy to EC2') {
      steps {
        sshagent(credentials: ['ubuntu']) {
          sh '''
            set -e

            scp -o StrictHostKeyChecking=no build.tgz ubuntu@ec2-16-16-160-0.eu-north-1.compute.amazonaws.com:~/

            ssh -o StrictHostKeyChecking=no ubuntu@ec2-16-16-160-0.eu-north-1.compute.amazonaws.com '
              set -e
              mkdir -p /opt/calculator-app
              tar xzf ~/build.tgz -C /opt/calculator-app
              cd /opt/calculator-app
              python3 -m venv venv || true
              . venv/bin/activate
              pip install --upgrade pip
              pip install -r requirements.txt
              pip install gunicorn
              sudo systemctl restart calculator
            '
          '''
        }
      }
    }
  }

  post {
    always {
      echo 'Cleaning up workspace...'
      cleanWs(deleteDirs: true)
    }
    success {
      echo '✅ Build and deploy succeeded.'
    }
    failure {
      echo '❌ Build or deploy failed.'
    }
  }
}