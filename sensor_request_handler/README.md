## Introduction
Module that interacts with kafka pipeline and exposes sensor data as an API.

## Environment
Requires kafka, mongo and all sensors in config to be up and running.

## Python Module
``` python3 -m sensor_request_handler```

## Docker Image
```
docker build -t sensor_request_handler .
docker run --detach --name sensor_request_handler --network host sensor_request_handler:latest
```
