<h1>Anoroc</h1>

This project is for the course <i> Digitala System</i>  EITA15, at Lunds University.

The purpose of the project was to build a radio-controlled vehicle that could be controlled from a host computer. The MCU that had to be used was an 8-bit AVR ATMega1284 MCU. The vision was also to live-stream video from the vehicle to the computer.

After several months of work the project did succeed. 


<h2>Steering </h2>
The steering is controlled with a Bluetooth-module, connected with the MCU. This Bluetooth-module gets commands from the PC, running a Python script.

<h2>Video-stream</h2>
The video-stream is handled with the help of a Raspberry Pi W Zero, using a Raspberry Pi Camera v2 module. The Pi connects to the PC, which is running a Hotspot, and then starts to transfer video-data over a TCP-connection.

<h2>Chassis</h2>
The chassis of the vehicle was made with a 3D-printer, using Blender

<h2>Anoroc, the one and only</h2>

![Image of Anoroc](https://github.com/victorhook/projekt_eita15/blob/master/anoroc.jpg)
