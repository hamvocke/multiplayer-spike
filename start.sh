#! /usr/bin/env bash

pipenv run gunicorn --bind=0.0.0.0 -k flask_sockets.worker app:app
