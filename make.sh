#!/bin/bash

sudo docker container rm node
sudo docker image rm node

sudo docker build -t node .
sudo docker run --device=/dev/ttyUSB0 --name node node
