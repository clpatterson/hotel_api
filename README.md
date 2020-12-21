# Asteroid Hotels REST API
![GitHub Actions status | build](https://github.com/clpatterson/hotel_api/workflows/build/badge.svg)
## Introduction
The Asteroid Hotels REST API is a reservation system for a fictitious hotel group,
the Asteroid Group. The Asteroid Group operates hotels on select asteroids in
the solar system. Using the API, users can search hotels and make reservations. The API is live and Swagger documentation can be found at [astrdhotels.com](https://astrdhotels.com/api/v0.1/docs).

The API is built with Flask-RESTX, SQLAlchemy, PyJWT, PyEphem, Postgres, and Docker. The API web service is deployed on GCP Cloud Run. The Postgres database runs on a f1-micro Compute Engine instance to take advantage of the free tier. Github Actions is used for continuous integration. This repo is mirrored in Cloud Source Repositiories and Cloud Build is used for continuous deployment. 

## Getting Started: Local Development

1. Clone repo locally
```bash
git clone https://github.com/clpatterson/hotel_api.git
```
2. Start up local development environment in project root directory
```bash
docker-compose up --build
```
3. Initialize and seed the database with cli command
```bash
docker-compose exec api hotel_api db reset --with-testdb --dev
```
4. Run integration and unit tests
```bash
docker-compose exec api py.test tests/
```
