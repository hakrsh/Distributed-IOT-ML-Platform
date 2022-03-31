## Introduction
Module that interacts with sensors and pushes data to kafka pipeline

## Environment
Requires kafka, mongo and all sensors in config to be up and running.

## Python Module
``` python3 -m sensor_manager```

## Docker Image
```
docker build -t sensor_manager .
docker run --detach --name sensor_manager --network host sensor_manager:latest
```
