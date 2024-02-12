#!/bin/sh

source .venv/bin/activate
pip freeze > requirements.txt
