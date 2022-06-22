# Digest-web Backend service

Django based backend service for the DIGEST web-app.

## Setup

Pull all docker images from dockerhub

`docker-compose pull`

## Environment

Create a local copy of the environment file and <b>do not<b> push it to the git.

`cp docker-django-example.env.dev docker-django.env.dev`

Adjust the secret passwords, keys and settings accordingly. It will be used to hand this secret information to all
containers without writing them into the code.

## Rebuild

Build local docker images

`docker-compose build`

## Deployment

Create containers for all images defined in docker-compose.yml file and run detached

`docker-compose up -d`

## Development hints

Show running docker containers:

`docker ps`

Follow log of selected container:

`docker logs -f $container_name`

