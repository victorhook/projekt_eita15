from vc0706_reg import *
import os
import serial
import struct
import sys
import time

DEFAULT_PORT         = '/dev/ttyUSB0'
DEFAULT_BAUD         = 38400
DESIRED_BAUD         = 115200

PROTOCOL             = 0x56
SERIAL_NBR           = 0x00

IMG_RES_640x480      = 0x00
IMG_RES_320x240      = 0x11
IMG_RES_160_120      = 0x22

BAUD_9600            = [0xae, 0xc8]
BAUD_19200           = [0x56, 0xe4]
BAUD_38400           = [0x2a, 0xf2]
BAUD_57600           = [0x1c, 0x1c]
BAUD_115200          = [0x0d, 0xa6]

BAUDS                = {9600:BAUD_9600, 19200:BAUD_19200, 38400:BAUD_38400, 
                                        57600:BAUD_57600, 115200:BAUD_115200}

PKT_GET_VERSION      = [PROTOCOL, SERIAL_NBR, GEN_VERSION, 0x00]
PKT_RESTART          = [PROTOCOL, SERIAL_NBR, SYSTEM_RESET, 0x00]
PKT_SET_BAUD         = [PROTOCOL, SERIAL_NBR, SET_PORT, 0x03, 0x01] # + baud rate (2 bytes)
PKT_STOP_CURR_FBUF   = [PROTOCOL, SERIAL_NBR, FBUF_CTRL, 0x01, 0x00]
PKT_START_CURR_FBUF  = [PROTOCOL, SERIAL_NBR, FBUF_CTRL, 0x01, 0x02]
PKT_GET_FBUF_LEN     = [PROTOCOL, SERIAL_NBR, GET_FBUF_LEN, 0x01, 0x00]
PKT_READ_FBUF        = [PROTOCOL, 0x00, READ_FBUF, 0x0c, 0x00, 0x0a, 0x00, 0x00, 
                                  0x00, 0x00, 0x00, 0x00, None, None, 0x01, 0x00]       
PKT_SET_IMG_SIZE     = [PROTOCOL, SERIAL_NBR, WRITE_DATA, 0x05,  0x04, 0x01, 0x00, 0x19] # + IMG SIZE (1 byte)
PKT_READ_IMG_SIZE    = [PROTOCOL, SERIAL_NBR, READ_DATA, 0x04,  0x04, 0x01, 0x00, 0x19]


DEFAULT_REPLY_SIZE   = 5
STATUS_OK            = 0
TIMEOUT              = 0.2

IMAGE_DIR            = os.path.join(os.path.dirname(__file__), 'images')

class VC0706:

    def __init__(self, port=DEFAULT_PORT, baud=DESIRED_BAUD):

        self.stream        = None
        self.port          = port
        self.baud          = baud
        self.dir           = IMAGE_DIR
        self.save_image    = False
        self.timeout       = TIMEOUT
        self.images_taken  = 0

    def save(self, photo):
        #self.images_taken += 1
        with open(os.path.join(self.dir, 'images%s.jpg' % self.images_taken), 'wb') as f:
            f.write(bytearray(photo))
        

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        if self.stream:
            self.stream.close()

    """ Tries to connect to the VC0706 through serial port """
    def connect(self):
        if not self.stream:
            try:
                self.stream = serial.Serial(self.port, self.baud, timeout=self.timeout)
                self.stream.flush()
                print('Connected to VC0706 on port %s' % self.port)
                
                self.get_version()
                # Everything OK, ready to go!
                #print('Baud rate: %s' % self.baud)

            except Exception as e:
                print(e.with_traceback())
                print("Can't connect to port")
                sys.exit(0)

    """ Set baud rate to the new and restart the camera """
    def set_baud_rate(self, baud):
        self.baud = baud
        self.stream.flush()

        packet = PKT_SET_BAUD
        packet.append(BAUDS[baud][0])
        packet.append(BAUDS[baud][1])
        self.send(packet)
        
        status = self.read(5)

            # Try again
        if status[3] != STATUS_OK:

            self.stream.flush()
            self.send(packet)
            if status[3] != STATUS_OK:
                print('Failed to change baud rate, exiting...')
                sys.exit(0)


        self.stream.close()
        time.sleep(0.001)
        self.stream = self.open()


    def stop_fbuf(self):
        self.stream.write(PKT_STOP_CURR_FBUF)
        cmd, status, d_len = self._read_packet()
        if status != STATUS_OK:
            print('Problem stoppning fbuf')

    def start_fbuf(self):
        self.stream.write(PKT_START_CURR_FBUF)
        cmd, status, d_len = self._read_packet()
        if status != STATUS_OK:
            print('Problem starting fbuf')


    def get_fbuf_len(self):
        self.stream.write(PKT_GET_FBUF_LEN)
        cmd, status, d_len = self._read_packet()
        if status != STATUS_OK:
            print('Problem reading fbuf')

        return self.stream.read(d_len)


    def read_fbuf(self, size):
        PKT_READ_FBUF[-3] = size[3]
        PKT_READ_FBUF[-4] = size[2]
        self.stream.write(PKT_READ_FBUF)

        status = self._read_packet()[1]
        if status != STATUS_OK:
            print('Error reading frame buffer!')
            return

       
        index = 0
        image_length = int.from_bytes(size, 'big')

        photo = []
        
        end = int(image_length / 32)
        remainder = image_length % 32

        while index < end:
            photo += self.stream.read(32)
            index += 1

        photo += self.stream.read(remainder)


        status = self._read_packet()[1]
        if status != STATUS_OK:
            print('Error reading frame buffer!')
            return

        #photo = ' '.join('{:02X}'.format(b) for b in photo)
        
        return photo


    def enable_save(self):
        self.save_image = True

    def disable_save(self):
        self.save_image = False


    def get_version(self):
        
        self.send(PKT_GET_VERSION)
        reply = self.stream.read(5)    

            # Probably wrong baud rate, try reconnect with default settings!
        if not reply:
            self.baud = DEFAULT_BAUD
            self.stream.close()
            self.stream = serial.Serial(self.port, self.baud, timeout=self.timeout)

            self.send(PKT_GET_VERSION)
            reply = self.stream.read(5)        

            if not reply or reply[3] != STATUS_OK:
                print('Error connecting to camera, check wiring/settings')
                sys.exit(0)


            # Try to change baudrate to desired (High speed, 115200) and reconnect
            self.baud = DESIRED_BAUD
            self.stream.flush()
            self.set_baud_rate(DESIRED_BAUD)
            self.stream.close()
            self.stream = self.open()

            self.send(PKT_GET_VERSION)
            reply = self.stream.read(5) 

            if not reply or reply[3] != STATUS_OK:
                print('Failed to run at full speed, using default baud rate (38400)...')
                return
            
        version = self.read(reply[2])
        
#        print('Version:    %s' % version.decode())
 #       print('Baud rate:  %s' % self.baud)

            
    def open(self):
        return serial.Serial(self.port, self.baud, timeout=self.timeout)


    def _get_version(self):

        self.stream.flushInput()

        self.stream.timeout = 0.2
        status = None

        self.stream.write(PKT_GET_VERSION)

        try:
            cmd, status, d_len = self._read_packet()
        
        except:
            # Wrong baudrate, try default!
            self.baud = DEFAULT_BAUD
            self.stream.baudrate = self.baud

            try:
                cmd, status, d_len = self._read_packet()
            except Exception as e:
                print('Error communicating with VC0706. Check baud rate or wiring')
                sys.exit(0)


            # If default works, set baud rate to requested!
            baud_ok = self.set_baud_rate(DESIRED_BAUD)

            if baud_ok:
                self.baud = DESIRED_BAUD
            else:
                print("Can't change the baud rate, using default ...")
        

        if status == STATUS_OK:
            data = self.stream.read(d_len)
            print('Version: %s' % data.decode())
        else:
            print('Error getting version')
  
    
    def send(self, packet):
        if self.stream:
            self.stream.write(packet)
        
    def read(self, len):
        if self.stream:
            return self.stream.read(len)

    def _read_packet(self):
        return self.stream.read(DEFAULT_REPLY_SIZE)[2:]

    def set_img_size(self, size):
        packet = PKT_SET_IMG_SIZE
        packet.append(size)
        self.send(packet)

    def get_img_size(self):
        self.send(PKT_READ_IMG_SIZE)
        reply = self.read(6)
        if reply[3] == STATUS_OK:
            return reply[5]
        else:
            print('Failed to get the image size')

    def photo(self):
       
        self.stop_fbuf()

        d_len = self.get_fbuf_len()

        photo = self.read_fbuf(d_len)

        self.start_fbuf()

        if self.save_image:
            print('Saving photo')
            self.save(photo)

        return photo


    def restart(self):
        self.send(PKT_RESTART)
        time.sleep(.001)
        self.get_version()



    def pprint(self, packet): 
        print(' '.join('{:02X}'.format(b) for b in packet))



if __name__ == "__main__":

    with VC0706() as camera:
        camera.restart()
        