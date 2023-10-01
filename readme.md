# Book giveaway platform in FastAPI

This repository contains a FastAPI project for a bookgiveaway platform that can be easily set up and run using Docker Compose. It includes a Dockerized development environment for this FastAPI application.

## Prerequisites

Make sure you have the following software installed on your system:

- Docker: [Installation Guide](https://docs.docker.com/get-docker/)
- Docker Compose: [Installation Guide](https://docs.docker.com/compose/install/)

## Getting Started

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/Rati1324/book_giveaway.git
   ```
2. Build and start the Docker containers:

   ```bash
   docker-compose up --build
   ```
   This command will build the Docker images and start the containers defined in docker-compose.yml.

3. Access the FastAPI application in your browser:
    API documentation (Swagger): http://localhost:8000/docs
    Interactive ReDoc documentation: http://localhost:8000/redoc

    You can now interact with and test your FastAPI application using the provided documentation.

To stop the application and remove the Docker containers, press Ctrl+C in the terminal where docker-compose up is running, and then run:
   
   ```bash
   docker-compose down
   
