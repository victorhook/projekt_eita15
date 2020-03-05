from vc0706_reg import *
import os
from serial import Serial
from serial.serialutil import SerialException
import struct
import sys
import time

PORT_DEFAULT         = '/dev/ttyUSB0'
BAUD_DEFAULT         = 38400
BAUD_HIGH_SPEED      = 115200

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
                                  0x00, 0x00, 0x00, 0x00, None, None, 0x22, 0x00]       
PKT_SET_IMG_SIZE     = [PROTOCOL, SERIAL_NBR, WRITE_DATA, 0x05,  0x04, 0x01, 0x00, 0x19] # + IMG SIZE (1 byte)
PKT_READ_IMG_SIZE    = [PROTOCOL, SERIAL_NBR, READ_DATA, 0x04,  0x04, 0x01, 0x00, 0x19]


DEFAULT_REPLY_SIZE   = 5
STATUS_OK            = 0
TIMEOUT              = 0.2

IMAGE_DIR            = os.path.join(os.path.dirname(__file__), 'images')
IMAGE_NAME           = 'RaceCar'



class VC0706():

    def __init__(self, port=PORT_DEFAULT, baud=BAUD_HIGH_SPEED, timeout=TIMEOUT):
        
        self.port          = port
        self.baud          = baud
        self.timeout       = TIMEOUT

        self.dir           = IMAGE_DIR
        self.image_name    = os.path.join(self.dir, '%s.jpg' % IMAGE_NAME)
        self.save_image    = True
        self.version       = None

        self.err_handle    = sys.exit       # Error handling can be configured
        self.stream        = None


    def get_image_path(self):
        return self.image_name

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        if self.stream:
            self.stream.close()
            self.stream = None


    """ Tries to connect to the VC0706 through serial port 
        and sets the baud rate to highets (115200) """
    def connect(self):

        if not self.stream:

            # If port is open we connect, otherwise we call error handler
            try:
                self.stream = Serial(self.port, self.baud, timeout=self.timeout)
                

            except SerialException as e:
                    print("Can't open port %s" % self.port)
                    self.err_handle()

            print('Connected on port %s' % self.port)

            if self.communication_ok():

                self.version = self.get_version()
                print('[VC0706] Version:   %s' % self.version)
                print('[VC0706] Baud rate: %s' % self.baud)
                
                if self.baud != BAUD_HIGH_SPEED:
                    self.set_baud_rate(BAUD_HIGH_SPEED)

            else:
                self.err_handle()


    """ Returns the current version of the camera """
    def get_version():
        if self.stream:
            self.send(PKT_GET_VERSION)
            ack = self.read(5)
            if self.ack_ok(ack):
                version = self.read(reply[4])
                print(version.decode())
            else:
                print('Error getting version!')
                self.err_handle()


    """ Finds the baud rate  that the camera currently is using and
        adjusts the serial port accordingly. If no baud rate matches,
        we return false to let caller handle the error              """
    def communication_ok(self):
        for baud in BAUDS.keys():
            self.stream.baudrate = baud
            self.stream.write(PKT_GET_VERSION)
            reply = self.stream.read(5)
 
            if len(reply) == DEFAULT_REPLY_SIZE:
                self.stream.flushInput()
                return reply[3] == STATUS_OK
                    
        return False


    """ Set baud rate to the new and reconnect with camera """
    def set_baud_rate(self, baud):

        if self.baud != baud:
            self.baud = baud

        packet = PKT_SET_BAUD
        packet.append(BAUD_115200[0])
        packet.append(BAUD_115200[1])
        self.send(packet)

        self.stream.close()
        self.stream = Serial(PORT_DEFAULT, BAUD_HIGH_SPEED, timeout=TIMEOUT)
        self.stream.baudrate = BAUD_HIGH_SPEED

        self.stream.write(PKT_GET_VERSION)
        
        ack = self.read(5)
        if not self.ack_ok(ack):
            self.err_handle()


    def save(self, photo):
        with open(self.image_name, 'wb') as f:
            f.write(bytearray(photo))


    def stop_fbuf(self):
        self.send(PKT_STOP_CURR_FBUF)
        ack = self.read(DEFAULT_REPLY_SIZE)
        
        if not self.ack_ok(ack):
            print('Error stopping fbuf!')
            self.err_handle()

    def start_fbuf(self):
        self.send(PKT_START_CURR_FBUF)
        ack = self.read(DEFAULT_REPLY_SIZE)
        
        if not self.ack_ok(ack):
            print('Error starting fbuf!!')
            self.err_handle()

    def get_fbuf_len(self):
        self.stream.write(PKT_GET_FBUF_LEN)
        ack = self.read(DEFAULT_REPLY_SIZE)

        if not self.ack_ok(ack):
            print('Problem reading fbuf')
            self.err_handle()

        d_len = ack[4]
        return self.read(d_len)



    def read_fbuf(self, size):
        PKT_READ_FBUF[-3] = size[3]
        PKT_READ_FBUF[-4] = size[2]
        self.send(PKT_READ_FBUF)

        ack = self.read(DEFAULT_REPLY_SIZE)
        if not self.ack_ok(ack):
            print('Error reading FBUF!')
            self.err_handle()

        index = 0
        image_length = int.from_bytes(size, 'big')

        photo = []
        
        end = int(image_length / 32)
        remainder = image_length % 32

        while index < end:
            photo += self.read(32)
            index += 1

        photo += self.read(remainder)

        ack = self.read(DEFAULT_REPLY_SIZE)
        if not self.ack_ok(ack):
            print('Error in end of reading FBUF!')
            print(self.pprint(ack))
            self.err_handle()

        #photo = ' '.join('{:02X}'.format(b) for b in photo)
        
        return photo

    def ack_ok(self, ack):
        return len(ack) >= DEFAULT_REPLY_SIZE and ack[3] == STATUS_OK

    def enable_save(self):
        self.save_image = True

    def disable_save(self):
        self.save_image = False

    def get_version(self):

        self.send(PKT_GET_VERSION)
        cmd, status, d_len = self.read(DEFAULT_REPLY_SIZE)[2:]
        if status == STATUS_OK:
            return self.read(d_len).decode()
        else:
            self.err_handle()

    
    def send(self, packet):
        if self.stream:
            self.stream.write(packet)
        
    def read(self, len):
        if self.stream:
            return self.stream.read(len)

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


    def pprint(self, packet): 
        print(' '.join('{:02X}'.format(b) for b in packet))



if __name__ == "__main__":

    with VC0706() as camera:
        camera.photo()