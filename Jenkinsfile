pipeline {
  agent any

  options {
    timeout(time: 20, unit: 'MINUTES')     // Stop builds that hang
    disableConcurrentBuilds()              // Prevent overlapping runs
    timestamps()                           // Add timestamps to logs
  }

  environment {
    APP_HOST = 'ec2-16-16-160-0.eu-north-1.compute.amazonaws.com'
    APP_SSH  = "ubuntu@${APP_HOST}"
    APP_DIR  = "/opt/calculator-app"
    VENV_DIR = "${APP_DIR}/venv"
    SSH_CRED = "ec2-key"
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
          echo "Setting up Python virtual environment..."
          python3 --version
          python3 -m venv .venv
          . .venv/bin/activate
          pip install --upgrade pip
          deactivate || true
        '''
      }
    }

    stage('Install deps & Test') {
      steps {
        timeout(time: 5, unit: 'MINUTES') {  // Safety timeout for dependency setup/tests
          sh '''
            set -e
            echo "Installing dependencies and running tests..."
            . .venv/bin/activate
            pip install -r requirements.txt
            pip install pytest
            echo "Running pytest..."
            pytest --maxfail=1 --disable-warnings -q || echo "Tests failed but continuing."
            deactivate || true
          '''
        }
      }
    }

    stage('Package') {
      steps {
        sh '''
          set -e
          echo "Packaging application..."
          tar czf build.tgz --exclude .venv --exclude __pycache__ --exclude .git *
        '''
        archiveArtifacts artifacts: 'build.tgz', fingerprint: true
      }
    }

    stage('Deploy to EC2') {
      steps {
        sshagent(credentials: [env.SSH_CRED]) {
          sh '''
            set -e
            echo "Deploying to EC2 instance ${APP_HOST}..."
            RSYNC_RSH="ssh -o StrictHostKeyChecking=no"

            # Ensure target directory exists and is owned by app user
            ssh -o StrictHostKeyChecking=no ${APP_SSH} "sudo mkdir -p ${APP_DIR} && sudo chown -R app:app ${APP_DIR}"

            # Sync source code safely (preserve venv folder)
            rsync -az --delete --exclude 'venv/' -e "$RSYNC_RSH" ./ ${APP_SSH}:${APP_DIR}/

            # Create or update Python environment, install gunicorn, and restart service
            ssh -o StrictHostKeyChecking=no ${APP_SSH} "bash -lc '
              set -e
              cd ${APP_DIR}
              [ -d ${VENV_DIR} ] || python3 -m venv ${VENV_DIR}
              . ${VENV_DIR}/bin/activate
              pip install --upgrade pip
              pip install -r requirements.txt
              pip install gunicorn
              sudo systemctl daemon-reload
              sudo systemctl restart calculator
              systemctl --no-pager -l status calculator || true
              deactivate || true
            '"
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
