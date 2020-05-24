#from gui import Gui
from hotspot import Hotspot

import io
from PIL import ImageTk, Image
import socket
import struct
import sys
import re
import time
import threading
import tkinter as tk

class PiAnoroc:

    def __init__(self, gui, hotspot_name, addr, port, stop_flag, log):

        self.sock      = None        # Network socket
        self.ip        = None        # Client IP
        self.con       = None        # File-like object for read/write access through socket
        self.hotspot_name = hotspot_name
        self.port      = port        # TCP Port
        self.addr      = addr        # IP4 address
        self.log       = log
        
        self.gui       = gui         # Reference to the GUI to update image
        self.stop_flag = stop_flag        # Flag for synchronizing threads  

    """ 
        Tries to open a network socket to the given IP and port, and
        then waits for a connection to be made.
        This method is given its own thread and enters an infinite-loop
        (if connection is succesful) and only exits when the user clicks disconnect
    """
    def open(self):

        # Ensure that stop-flag is clear before we start!
        self.stop_flag.clear()
        self.log.info('Listening on port %s at address %s' % (self.port, self.addr))

        # Open socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Allow re-use of TCP port without needing to wait the TIME_WAIT delay
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.sock.bind((self.addr, self.port))
        except Exception as error:
            self.log.info('Failed to bind to port %s with address %s' % (self.port, self.addr))
            self.log.info('Python: {}'.format(error))
            return

        # Start listening for connections
        self.sock.listen(0)

        # Client accepted!
        try:
            client, addr = self.sock.accept()
            self.ip = addr[0]
            self.con = client.makefile('rb')  

            self.log.info('Connected to AnorocPi')
            self.run()

        except:
            # sock.accept() throws an exception if not finished
            # This only happens if we disconnect before client connects
            sys.exit(0)
 

    def close(self):
        self.log.info('Closing port %s' % self.port)

        try:
            if self.con:
                # Properly close the stream
                self.sock.shutdown(socket.SHUT_RDWR)
                self.sock.close()
            else:
                self.sock.shutdown(socket.SHUT_RDWR)
                self.sock.close()
                self.sock.detach()

        except Exception as error:
            # Failed to close socket and/or stream, not much to do
            self.log.info('Error when closing port %s' % self.port)
            self.log.info('Python: {}'.format(error))


        # Reset connection variables
        self.sock       = None
        self.ip         = None
        self.con        = None


    # Main thread for image capturing
    def run(self):

        # Variables for figuring out the fps
        timer  = time.time()
        fps    = 0

        # Buffer stream for handling input image
        img_stream = io.BytesIO()   

        self.log.info('Start streaming video...')

        # We keep updating the GUI frames as long as we're connected
        while not self.stop_flag.is_set():

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
            img = img.rotate(180)

            fps += 1

            # Update the FPS variable on the GUI
            if time.time() - timer >= 1:
                timer = time.time()
                self.gui.fps_update(fps)
                fps = 0


            # Update the gui
            self.gui.img_update(ImageTk.PhotoImage(img))
            self.gui.update()

            # Rewind the bytestream and truncate it, to make it ready to receivde new data
            img_stream.seek(0)
            img_stream.truncate()


        # We're done sampling frames, let's close the connections!
        #self.close()


    # Wrapper method
    def read_img_len(self):
        # Read a 32-bit integer from the connection
        return struct.unpack('<L', self.con.read(struct.calcsize('<L')))[0]

    """
        The class can be used with PiAnoroc() as ... :
        with the following methods. This ensures correct opening
        and closing of sockets
    """
    def __exit__(self, *_):
        self.close()

    def __enter__(self):
        self.open()
        print('open')
        return self