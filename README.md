# TrafficMonitor
==============

TrafficMonitor tries to detect the amount of traffic in an image. It is designed for very low-resolution images, and as such does not use a car-detection detection algorithm, but rather a general feature detection algorithm on the difference between the current and the previous image from web cameras.

There are two versions in this repository:
* trafficmon.py is a standalone version, that uses two cameras around the University of Tromsø
* traffic_server.py is a web server that allows users to submit cameras, and view their collection of cameras using different algorithms, and subscribe to other nearby cameras (sorted by distance)


## Requirements
-------------

### trafficmon
* python 2.7
* pygame
* python-opencv
* numpy


### traffic_server
* python 2.7
* python-opencv
* flask
* gdbm
* numpy

## Using the system
------------------

To run the system, simple run `python trafficmon.py` or `python traffic_server.py`. The server runs on localhost:5000 by default.