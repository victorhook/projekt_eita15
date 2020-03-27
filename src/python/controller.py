from bluepy.btle import *
from callback import Callback
from logger import Log

import threading

SCAN_TIMEOUT   = 1
TARGET_MAC     = '50:65:83:0e:9d:5d'
USART_HANDLER  = 37

BASE           = 'GUI/'
LOG_OUTPUT     = BASE + 'log/log'

if __name__ == '__main__':

    import glob
    import logging
    import logging.handlers

    LOG_FILENAME = 'logging_rotatingfile_example.out'

    logger = logging.getLogger('TestLog')
    logger.setLevel(logging.INFO)

    handler = logging.FileHandler(LOG_FILENAME)

    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    logger.info("hey!")

class Controller(DefaultDelegate):

    def __init__(self):
        self.scan = Scanner()
        self.connected = False
        self.device = None
        self.usart = None

        """ Callbacks """
        # Called when bluetooth is connected
        self.connected = Callback()

        # Called when bluetooth is disconnected
        self.disconnected = Callback()

        # Called if the connection to bluetooth fails
        self.connection_failed = Callback()

        # Called if the target device can't be found
        self.device_not_found = Callback()

        # Called if there's already a connection with the target
        self.already_connected = Callback()

        # Called when a packet is received from the device
        self.packet_received = Callback()
        
        # Flag for thread-handing
        self.is_alive = False

        """ Default log settings """
        self.log = Log(mode='w+')
        self.log.info('Session started')


    """ Scans nearby devices and connects to the target if not 
        already connected. Also sets the usart handler to
        send and receive messages                           """                       
    def connect(self):

        if not self.connected:

            self.scan.scan(SCAN_TIMEOUT)

            for dev in self.scan.getDevices():      # Check if devices match target

                if dev.addr == TARGET_MAC:
                    
                    if dev.connectable:
            
                        self.device = Peripheral(dev)
                        self.device.setDelegate(self)
                        self.connected = True
                        self.connected.call()              
                        # self.gui.update_status('Connected to %s' % TARGET_MAC)

                        # Sets the correct handler for the usart
                        for char in self.device.getCharacteristics():
                            if char.getHandle() == USART_HANDLER:       
                                self.usart = char

                        self.gui.device_connected()
                        return

                    else:
                        self.connection_failed.call()       
                        #self.gui.update_status('Failed to connect to device')
                        return
            
            self.device_not_found.call()
            #self.gui.update_status('Device not found...')

        else:
            self.already_connected.call()
            #self.gui.update_status('Already connected')


    def send(self, packet):
        if not self.usart is None:
            self.usart.write(packet, True)


    def disconnect(self):
        if self.connected:
            self.device.disconnect()
            self.connected = False
            self.device = None
            self.usart = None   
   

    def run(self):
        self.is_alive = True

        while self.is_alive:
            pass

    def is_alive():
        return self.is_alive

    def kill(self):
        self.is_alive = False
        self.device = None

    # Callback from connected Peripheral
    def handleNotification(self, c_handle, data):
        self.packet_received(data)
        #self.gui.print(data)
        #print(data)


    # Callback from Low Energy device when scanner is active
    def handleDiscovery(self, scan_entry, is_new_dev, is_new_data):
        pass

if __name__  == '__main__':
    ct = Controller()
