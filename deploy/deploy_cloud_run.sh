#!/bin/bash
#
# Complete entire process for spinning up postgres container

# For debugging peurposes
set -o verbose
set -o errexit
set -o xtrace

# Create docker image and tag
docker build -f Dockerfile.production -t gcr.io/recurse-dev/hotel_api:latest -t gcr.io/recurse-dev/hotel_api:v0.1 .

docker push gcr.io/recurse-dev/hotel_api:latest

# Use image to spin up cloud run
gcloud run deploy <service_name> --image gcr.io/recurse-dev/hotel_api:latest \
--project recurse-dev \
--region us-central1 \
--platform managed \
--allow-unauthenticated \
--set-env-vars "SECRET_KEY=<secret_key>" \
--set-env-vars "POSTGRES_USER=<user>" \
--set-env-vars "POSTGRES_PASSWORD=<password>" \
--set-env-vars "POSTGRES_HOST=<host_ip_address>" \
--set-env-vars "PROD=true" \
--max-instances 2

# Update cloud run container with host name
gcloud run services update <service_name> \
--project recurse-dev \
--region us-central1 \
--platform managed \
--update-env-vars "SERVER_NAME=hotel-api-qjutfzv47q-uc.a.run.app"

# Setup a serverless vpc connector
gcloud services enable vpcaccess.googleapis.com

# Provision the connector
# See docs: https://cloud.google.com/run/docs/configuring/connecting-vpc
gcloud compute networks vpc-access connectors create crun-to-ceng \
--network default \
--region us-central1 \
--range 10.8.0.0/28

# Verify connector is ready
gcloud compute networks vpc-access connectors describe crun-to-ceng --region us-central1

# Attach connector to cloud run service
gcloud run services update <service_name> \
--project recurse-dev \
--region us-central1 \
--platform managed \
--vpc-connector crun-to-ceng
