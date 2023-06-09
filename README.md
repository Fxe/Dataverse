# Dataverse

[![Dataverse tests](https://github.com/EarthSystemsSciences/Dataverse/actions/workflows/test.yml/badge.svg)](https://github.com/EarthSystemsSciences/Dataverse/actions/workflows/test.yml)
[![Create and publish a Docker image](https://github.com/EarthSystemsSciences/Dataverse/actions/workflows/publish_image.yml/badge.svg)](https://github.com/EarthSystemsSciences/Dataverse/actions/workflows/publish_image.yml)

ESS data application

This project aims to build a web application using the FastAPI 
framework to interface with [KBase](https://www.kbase.us/), 
[ESGF](https://esgf.llnl.gov/), 
and [ARM](https://www.arm.gov/), 
allowing retrieval and saving of data objects.


## Usage

OpenAPI documentation is provided at the `/docs` endpoint of the server,
 and error codes are listed in [errors.py](src/service/errors.py).

## Development

### Running tests

Python 3.10 must be installed on the system to run the tests. 

Run the following commands to execute the tests:

```commandline
pipenv sync --dev  # only the first time or when Pipfile.lock changes
pipenv shell
PYTHONPATH=. pytest test
```

### Running server locally

The server can be run locally using Docker:

```commandline

docker-compose build
docker-compose up
```

```commandline
docker build -t dataverse .
docker stop dataverse; docker rm dataverse
docker run -d --name dataverse \
	-p 30015:8000 dataverse
```

The application can then be accessed at http://localhost:30015/docs.