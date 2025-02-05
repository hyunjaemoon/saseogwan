#!/bin/bash
gcloud config set project saseogwan
pip install -r requirements.txt
python3 server.py