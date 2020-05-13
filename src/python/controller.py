from callback import Callback

import bluepy.btle as bt
import struct
import threading
import time

import logging

SCAN_TIMEOUT   = 2
TARGET_MAC     = '50:65:83:0e:9d:5d'
USART_HANDLER  = 37
RCV_PKT_FORMAT = 'BBBBB'
SND_PKT_FORMAT = 'BBB'
PACKET_TIMEOUT = 2

"""
    The HM-10 BLE can be programmed with AT-commands
    AT => OK
    AT+HELP => INFO
    AT+BAUD => BAUD RATE
    AT+BAUD[0-8] => SET BAUD RATE
    AT+BAUD4 = 9600
    AT+BAUD8 = 115200
"""

class Controller(bt.DefaultDelegate):

    """

    """

    def __init__(self, log):

        self.device    = None
        self.stream    = None
        self.log       = log
        self.timer     = 0
        self.stop_flag = threading.Event()


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
        
        # Called to send a packet
        self.send_packet = Callback()

        # Called when timeout
        self.timeout = Callback()

        self.add_default_callbacks()


    def add_default_callbacks(self):
        self.connected.add_callback(lambda MAC: self.log.info('Connected to Bluetooth MAC %s' % MAC))
        self.connection_failed.add_callback(lambda: self.log.info('Connection failed'))
        self.device_not_found.add_callback(lambda: self.log.info('Device not found'))
        self.already_connected.add_callback(lambda: self.log.info('Already connected to %s' % self.device))


    """ Scans nearby devices and connects to the target if not 
        already connected. Also sets the usart handler to
        send and receive messages (like a socket stream)         """                       
    def connect(self):
        
        if self.device is None:       

            # Scans for nearby devices
            scan = bt.Scanner()
            scan.scan(SCAN_TIMEOUT)

            for dev in scan.getDevices():      
                
                # Check is target MAC is found
                if dev.addr == TARGET_MAC:
                    
                    if dev.connectable:
                        
                        # Make a connection to the target and set callbacks to bluepy API
                        # (This is done by inheriting DefaultDelegate class)
                        self.device = bt.Peripheral(dev)
                        self.device.withDelegate(self)

                        # Sets the correct handler for the usart (allows stream-like API)
                        for char in self.device.getCharacteristics():
                            if char.getHandle() == USART_HANDLER:       
                                self.stream = char

                        # Let the rest of the program know that we're connected!
                        self.connected.call(TARGET_MAC)              

                        # Start infinite-communication-loop
                        self.stop_flag.clear()
                        self.run()
                        
                        # Should not be reached
                        return

                    else:
                        self.connection_failed.call()       
                        return
            
            self.device_not_found.call()

        else:
            self.already_connected.call()


    def send(self, packet):
        if self.stream:
            self.stream.write(packet)


    def disconnect(self):
        if self.device:
            self.device.disconnect()
            self.device = None
            self.usart = None   
            self.disconnected.call()
   

    def __enter__(self):
        threading.Thread(target=self.connect).start()
        return self


    def __exit__(self, *args):
        self.stop_flag.set()
        self.disconnect()
        self.send('Exiting!')


    def run(self):

        try:
            # Make sure that we're still connected
            if self.device:

                # Enter infinite-loop, running as long as programs wants us to
                while not self.stop_flag.is_set():

                    try:
                        self.device.waitForNotifications(1)
                        if time.time() - self.timer >= PACKET_TIMEOUT:
                            self.timeout.call()
                            self.timer = time.time()
                        
                    except Exception as e:
                        self.disconnected.call()

            else:
                self.disconnected.call()

        finally:
            # We're done, let's disconnect
            self.disconnect()

    
    # Callback from connected Peripheral
    # c_handle is only needed if multiple devices are used
    def handleNotification(self, c_handle, data):
        try:
            data = struct.unpack_from(RCV_PKT_FORMAT, data)
            self.packet_received.call(data)
            self.send_packet.call()
        except Exception as e:
            self.log.info('Exception as BT: %s' % e)
        
        finally:
            self.timer = time.time()
