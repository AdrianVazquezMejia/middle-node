# Description
![example workflow](https://github.com/AdrianVazquezMejia/middle-node/actions/workflows/python-app.yml/badge.svg)
![Gitlab pipeline](https://gitlab.com/electr-nica/desarrollohardware/middle-node/badges/master/pipeline.svg)


This node collect data through LoRa from several edges-nodes or smart-meters.
# INDEX

* [Hardware tests](docs/hardware_test.md) 

# Installation

* Clone `git clone https://gitlab.com/electr-nica/desarrollohardware/middle-node`

* Go to the project folder `cd middle-node`

* Build `source make.sh`

* Run `sudo docker start node`

The serial port to  LoRa is set to *dev/ttyUSB0* by default, you can change that
in the config.json file before build or inside the container file system.

* To view the logs of the container `sudo docker container node --follow --since 0m`

* To stop it `sudo docker stop node`

#  Custom configuration

The folder json contains the config file where you can modify the default values for parameters.

# Collaborate

To develop you should not execute the *make.sh* file which is used for production purposes.
Instead, just develop through the source files (src folder) and a virtual environment of python 3. Remember to install the requirements before run.

tip: run from the parent folder because all path files are relative to this (ie. `python src/main.py`)
