# Dataverse
ESS data application


This project aims to build a web application using the FastAPI 
framework to interface with [KBase](https://www.kbase.us/), 
[ESGF](https://esgf.llnl.gov/), 
and [ARM](https://www.arm.gov/), 
allowing retrieval and saving of data objects.


## Usage

OpenAPI documentation is provided at the `/docs` endpoint of the server.

### Error codes

Error codes are listed in [errors.py](src/service/errors.py).

## Development

### Running tests

Python 3.10 must be installed on the system.

```commandline
pipenv sync --dev  # only the first time or when Pipfile.lock changes
pipenv shell
PYTHONPATH=. pytest test
```

### Running server locally

```commandline
docker build -t dataverse .
docker stop dataverse; docker rm dataverse
docker run -d --name dataverse \
	-p 8000:8000 dataverse
```
You should be able to access the server at http://localhost:8000/docs.