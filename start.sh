#! /usr/bin/env bash

pipenv run gunicorn -k flask_sockets.worker app:app
