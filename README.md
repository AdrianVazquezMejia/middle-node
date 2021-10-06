# Description
![example workflow](https://github.com/AdrianVazquezMejia/middle-node/actions/workflows/python-app.yml/badge.svg)
![Gitlab pipeline](https://gitlab.com/electr-nica/desarrollohardware/middle-node/badges/master/pipeline.svg)


This node collect data through LoRa from several edges-nodes or smart-meters.
# INDEX

* [Hardware tests](docs/hardware_test.md) 

# Installation

* Clone `git clone https://gitlab.com/electr-nica/2020-medidores-mesh/firmware/middle-node`

* Go to the project folder `cd middle-node`

* Build `source make.sh`

* Run `sudo docker start node`

The serial port to  LoRa is set to *dev/ttyUSB0* by default, you can change that
in the config.json file before build or inside the container file system.

* To view the logs of the container `sudo docker container node --follow --since 0m`

* To stop it `sudo docker stop node`

# On rapsberry pi Using the HAT.

The hat uses the UART0 as the way to communicate with the LORA module, so it is necesary to make some adjustments 
to the rpi in order to use it tha way.

* Open `sudo raspi-config` and select `Interface Options` then, at the option `P6` about "Serial Port" select `Yes` and lasty `No` to the presented options. That to allow the usage of the UART for general purpose.

* Edit the config file `sudo nano /boot/config.txt` and enable the uart verifing the line `enable_uart=1`, and disable the bluetooth `dtoverlay=disable-bt`

* Reboot the rpi `sudo reboot`.

* Verify that "json/config.json" at middle-node is set to the serial port related to the uart, that could vary depending on what rpi you are using: serial0,AMA0 or S0. Try and test.

* Verify the serial port in the Dockerfile.




#  Custom configuration

The folder json contains the config file where you can modify the default values for parameters.

Before build the container make sure the dockerfile contains the timezone corresponding to your location.

# Collaborate

To develop you should not execute the *make.sh* file which is used for production purposes.
Instead, just develop through the source files (src folder) and a virtual environment of python  Remember to install the requirements before run.

tip: run from the parent folder because all path files are relative to this (ie. `python src/main.py`)

# Trouble Shooting

1. The interrumption
2. The Scada Posting
3. CR
4. USB
5. Logs
