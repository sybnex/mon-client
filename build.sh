#!/bin/bash
set -e

APP="sybex/monitor-client"

docker build -t $APP .
docker push $APP
