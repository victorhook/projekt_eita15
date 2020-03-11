from serial import Serial
from tkinter import *
import time

PORT = '/dev/ttyUSB1'
BAUD = 9600


class OV7670:

    def __init__(self, port=PORT, baud=BAUD, timeout=5):
        self.stream = Serial(port, baud, timeout=timeout)

    def write(self, msg):
        self.stream.write(msg)

    def read(self):
        return self.stream.read(0xffffff)

    
if __name__ == "__main__":
   
    cam = OV7670(PORT, baud=38400)
    cam.write(b'\x07')
    data = cam.read()
    print(data)
    