#!/bin/bash
set -e

IMAGE_TAG=$1
MANIFESTS_REPO="https://${GIT_USER}:${GIT_TOKEN}@github.com/crazyfrog46/flask-calculator-manifests.git"

rm -rf manifests-tmp
git clone "$MANIFESTS_REPO" manifests-tmp
cd manifests-tmp

sed -i "s|image: crazyfrog46/flask-calculator:.*|image: crazyfrog46/flask-calculator:${IMAGE_TAG}|" deployment.yaml

git config user.email "jenkins@flask-calculator.local"
git config user.name "Jenkins CI"

git add deployment.yaml
git commit -m "Update image tag to ${IMAGE_TAG}" || echo "No changes to commit"
git push

cd ..
rm -rf manifests-tmp