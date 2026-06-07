#!/bin/bash
# Deploy PuckMind to Google Cloud Run (build locally)

set -e

# Configuration
PROJECT_ID="gen-lang-client-0367305329"
REGION="us-central1"
SERVICE_NAME="puckmind"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "🏒 Deploying PuckMind to Google Cloud Run (local build)..."
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo ""

# Set the project
echo "Setting GCP project..."
gcloud config set project ${PROJECT_ID}

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Configure Docker to use gcloud
echo "Configuring Docker authentication..."
gcloud auth configure-docker

# Build the container image locally
echo "Building container image locally..."
docker build -t ${IMAGE_NAME} .

# Push to Google Container Registry
echo "Pushing image to GCR..."
docker push ${IMAGE_NAME}

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10 \
  --set-env-vars MONGODB_URI=${MONGODB_URI} \
  --set-env-vars GOOGLE_CLOUD_PROJECT=${PROJECT_ID} \
  --set-env-vars GOOGLE_CLOUD_LOCATION=${REGION}

echo ""
echo "✅ Deployment complete!"
echo "Your app is now running at:"
gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)'
