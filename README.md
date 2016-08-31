# Garage Door

This is intended to be run on a Raspberry Pi 2/3.  I haven't tested it on anything earlier.  

## Overview

1. (optional, for some) Install Vim.
1. (optional) Install MQTT Clients. (Used for testing/validation)
1. Install RPi.GPIO
1. Install Paho, Python MQTT client libraries.

## Steps
These steps are executed on the Raspberry Pi.  If you prefer to take it step-by-step execute each line successively.  You may have a better chance at troubleshooting anything that goes wrong if you do it this way.
~~~~
$ sudo apt-get install vim
$ sudo apt-get install mosquitto-clients
$ sudo apt-get install RPi.GPIO
$ sudo apt-get install python-pip
$ sudo pip install paho-mqtt
~~~~
If you are feeling lucky, you can install it all at once.  Might be tricky to troubleshoot if it fails a dependency and you are not familiar with linux package management.
~~~~
$ sudo apt-get install vim mosquitto-clients RPi.GPIO python-pip; sudo pip install paho-mqtt
~~~~
