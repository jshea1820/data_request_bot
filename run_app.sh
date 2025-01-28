#!/bin/bash

pipenv run uvicorn graph_api.app:app --port 8008 &
pipenv run shiny run ./web_server/app.py --host 0.0.0.0 --port 8000
