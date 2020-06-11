#!/bin/bash
#
# Complete entire process for spinning up postgres container

# For debugging peurposes
set -o verbose
set -o errexit
set -o xtrace

### Get docker image and push to Google Cloud Registry
# Pull latest postgres docker image
docker pull postgres

# Tag the local image with the cloud registry name.
docker tag postgres gcr.io/recurse-dev/postgres

# Push the tagged image to cloud registry.
docker push gcr.io/recurse-dev/postgres

# Set firewall rules (only needs to be done once)
# gcloud compute firewall-rules create allow-postgres --allow tcp:5432 --target-tags postgres --project recurse-dev

### Spin up compute engine virtual machine with container configured and running w/ our image
# Spinup n1-standard-1 (default / $25 a month) vm with postgres container
gcloud compute instances create-with-container hotel-api-postgres \
--tags postgres \
--project recurse-dev \
--zone us-central1-b \
--container-image gcr.io/recurse-dev/postgres \
--container-env-file ./env.txt \
--container-mount-host-path host-path=$HOME/docker/volumes/postgres/,mount-path=/var/lib/postgresql/data/,mode=rw

# Open an interactive terminal to interface with postgres database
# docker exec -it <container-id> psql -U admin -d hotel_api