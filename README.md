# Solution

## Overview
This project is a FastAPI application that uses PostgreSQL as an event store. The API provides a single route, `/event`.
I have provided a Dockerfile to containerize the application and a `docker-compose.yml` file to manage the PostgreSQL database and the dependency between that and the FastAPI application.

## Prerequisites
Before running the application, ensure you have the following installed:
- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Python 3.12+](https://www.python.org/) (for running tests locally)

## How to Run the Application
To start the application using Docker Compose, run the following command:
```bash
docker-compose up --build -d
```
This will start the FastAPI application and PostgreSQL database. The API will be available at [http://127.0.0.1:8000/event](http://127.0.0.1:8000/event).

There will be a swagger UI available on http://127.0.0.1:8000/docs

To stop the application and remove the associated volumes, use:
```bash
docker-compose down --volumes
```

## Testing
A suite of unit tests is provided to verify the application's functionality. To run the tests, use:
```bash
pytest
```

## Project Structure
```
mn_tt/
│
├── src/
│   ├── __init__.py
│   ├── main.py          # FastAPI application entry point
│   ├── models.py        # Database models
│   ├── database.py      # Database connection and configuration
│   └── schema.py        # Pydantic schemas for request/response validation
│
├── tests/
│   ├── __init__.py
│   └── test_main.py     # API endpoint tests
│
├── Dockerfile           # Container configuration
├── docker-compose.yml   # Multi-container setup
└── README.md           # Project documentation
```

