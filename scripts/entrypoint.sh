#!/bin/bash

export DATAVERSE_DEPLOYMENT_CONFIG=dataverse_config.toml

jinja dataverse_config.toml.jinja -X "^DATAVERSE_" > $DATAVERSE_DEPLOYMENT_CONFIG

# FastAPI recommends running a single process service per docker container instance as below,
# and scaling via adding more containers. If we need to run multiple processes, use guvicorn as
# a process manger as described in the FastAPI docs
exec uvicorn --host 0.0.0.0 --port 8000 --factory src.service.app:create_app