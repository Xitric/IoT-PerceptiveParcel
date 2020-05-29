# Perceptive Parcel
This repository contains the source code for a project in the course Internet of Things at the University of Southern Denmark. The repository is split into two parts: an edge to be deployed on an ESP32 Azure IoT device, and a cloud to be deployed on a web server.

## Edge
The edge is developed using MicroPython. The code assumes that the device has access to WiFi. Currently, the file `Edge/main.py` contains hard-coded credentials for an Android access point, which will likely need to be changed.

Once the device powers on, it will listen for a package ID from the cloud (see below). Once a package ID has been received, the device will listen for setpoint values, after which it will begin communicating with the cloud.

## Cloud
The cloud has been developed using Flask for Python, and is currently hosted [here](https://d4f5817e.eu.ngrok.io/ "Perceptive Parcel Track & Trace") (will be taken down by July 2020). For a demo, the package IDs `vKT4UhLCcvjg` and `uvsrk6Ifra1g` may be used.

The [admin panel](https://d4f5817e.eu.ngrok.io/admin "Perceptive Parcel Admin Panel") is used to publish new package IDs to devices. This requires knowledge of the machine ID of the ESP32 device. Furthermore, the user must specify the type of package that is carried by the device. Loading the admin panel can be a little slow the first time it is accessed due to a query against the ontology.
