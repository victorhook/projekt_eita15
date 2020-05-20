The structure of the source files can be divided by Python and C.

<h2>Firmware</h2>
The firmware is written in C and consists of 4 modules:

* **globals** - Contains global variables and macros
* **drivers** - Contains drivers for sensors, IO, timers, interrupts and other functionality
* **usart**    - Small library for making usart-communication a breeze
* **main** - Here goes the main program, which imports the other modules, initializes the drivers, interrupts, timers, IO and the enters an infinite-loop where it :
	* Communicates with host
	* Update IO
	* Update variables

<h2>PC-side</h2>
The PC-side is using Python as well as Linux utilities, such as NetworkManager and BlueZ.
The Python code consists of x modules:

* **anoroc** - Class representation of the vehicle, consisting of variables with direction etc.
 * **callback** - Used by the **controller**, to attach callback functions for certain actions, disconnect, connect 
* **controller** - This is the bluetooth-controller which is built upon the [BluePy](https://github.com/IanHarvey/bluepy) library, which builds on BlueZ. The Controller class allows an abstract socket-like API to the bluetooth communication
etc.
* **gui** - Main GUI application, this is built with tkinter
* **handcontrol** - Small script that allows control of the car with the help of a MCU, with a joystick. In this implementation, a NodeMCU was used, running MicroPython, communicating over Wifi.
* **hotspot** - Functions to enable hotspot, essentially just runs cli commands using NetworkManager
* **logger** - Simple Logger wrapper
* **pi_anoroc** - This is the Raspberry Pi-video-streaming-controller, which opens a network socket and waits for a connection from the Raspberry Pi. 

<h2>Raspberry Pi</h2>

* An explanation and overview of how the Raspberry Pi works can be found [here](https://github.com/victorhook/projekt_eita15/tree/master/src/python/pi) 
