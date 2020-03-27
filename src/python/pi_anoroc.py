from gui import Gui

import io
from PIL import ImageTk, Image
from subprocess import Popen, PIPE
import socket
import struct
import sys
import re
import time
import threading
import tkinter as tk


HOTSPOT_NAME = 'Anoroc'
HOST_ADDR    = '192.168.0.7'
PORT         = 13337
IP_PATTERN   = '10.42.0.\d{1,3}'

# Scan for devices nmap -sP 10.42.0.0/24


class HotSpot:
    
    @staticmethod
    def open_hotspot():
        # Clears arp cache
        


        pipe = Popen(['iw', 'dev'], stdout=PIPE, stdin=PIPE, stderr=PIPE)
        status = str(pipe.stdout.read())

        # Checking if we're already runnig hotspot first!
        if HOTSPOT_NAME not in status:
            # Open hotspot
            Popen(['nmcli', 'connection', 'up', HOTSPOT_NAME], stdout=PIPE, stdin=PIPE, stderr=PIPE)

        # Hotspot should be up and running

    @staticmethod
    def close_hotspot():
        # Close hotspot, catch error msg in stderr, nothing to do with it.
        # nmcli handles any potential issues
        Popen(['nmcli', 'connection', 'down', HOTSPOT_NAME], stdout=PIPE, stdin=PIPE, stderr=PIPE)

    @staticmethod
    def get_connected_ip():
        # Check the arp cache for known IP addresses
        pipe = Popen(['arp', '-a'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        stdout = str(pipe.stdout.read())

        # Try to match found IP addressees with the expected one for the hotspot
        connected_ips = re.compile(IP_PATTERN).finditer(stdout)

        # Returns a list of IP addresses connected to hotspot (Should only be one)
        return [ip.group() for ip in connected_ips]


class PiAnoroc:

    def __init__(self, gui, port=PORT, addr=HOST_ADDR):

        self.sock      = None        # Network socket
        self.ip        = None        # Client IP
        self.con       = None        # File-like object for read/write access through socket
        self.port      = port        # TCP Port
        self.addr      = addr        # IP4 address
        
        self.gui       = gui         # Reference to the GUI to update image
        self.stop_flag = None        # Flag for synchronizing threads  


    """ Tries to open a network socket to the given IP and port, and
        then waits for a connection to be made                          
    """
    def open(self, stop_flag):

        self.stop_flag = stop_flag

        # Open socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.sock.bind((HOST_ADDR, PORT))
        except:
            print('Failed to bind to port %s with address %s' % (PORT, HOST_ADDR))
            sys.exit(0)

        # Start listening for connections
        self.sock.listen(0)

        # Client accepted!
        con, addr = self.sock.accept()
        self.ip = addr[0]
        self.con = con.makefile('rb')       

        print('Connected to %s on port %s' % (self.ip, PORT))

        self.run()
 
    def close(self):
        try:
            self.sock.close()
            self.con.close()
        except:
            # Failed to close socket and/or stream, not much to do
            pass

        # Reset connection variables
        self.sock       = None
        self.ip         = None
        self.con        = None
        self.stop_flag  = None


    # Main thread for image capturing
    def run(self):

        timer  = time.time()
        fps    = 0

        img_stream = io.BytesIO()   # Buffer stream for handling input image

        while not self.stop_flag.is_set():

            t_start = time.time()     # Counter, used for calculating fps

            # Read data length of current image frame
            img_len = self.read_img_len()

            # If length of image = 0, we're done!
            if not img_len:
                break
            
            # Put image data into stream buffer
            img_stream.write(self.con.read(img_len))

            # Rewind the stream to start
            img_stream.seek(0)
            img = Image.open(img_stream)

            fps += 1

            # Update the FPS variable on the GUI
            if time.time() - timer >= 1:
                timer = time.time()
                self.gui.fps_update(fps)
                fps = 0


            self.gui.img_update(ImageTk.PhotoImage(img))
            self.gui.update()

            img_stream.seek(0)
            img_stream.truncate()


        # We're done sampling frames, let's close the connections!
        self.close()


    def read_img_len(self):
        # Read a 32-bit integer from the connection
        return struct.unpack('<L', self.con.read(struct.calcsize('<L')))[0]


    def __exit__(self, *_):
        self.close()

    def __enter__(self):
        # Open connection and return a reference to the newly created object
        self.open()
        return self


if __name__ == "__main__":

    #HotSpot.open_hotspot()

    gui = Gui()
    gui.set_pi_anoroc(PiAnoroc(gui))
    
    

    gui.mainloop()
