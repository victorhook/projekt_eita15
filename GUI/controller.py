from bluepy.btle import *
import threading

SCAN_TIMEOUT = 1
TARGET_MAC = '50:65:83:0e:9d:5d'
USART_HANDLER = 37

class ErrorMessage:
    DEVICE_NOT_FOUND = 0
    FAILED_TO_CONNECT = 1
    DEVICE = None

class Controller(DefaultDelegate):

    def __init__(self, gui):
        self.scan = Scanner()
        self.connected = False
        self.device = None
        self.usart = None
        self.gui = gui
        
        # Flag for thread-handing
        self.is_alive = False


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
                        self.gui.update_status('Connected to %s' % TARGET_MAC)

                        # Sets the correct handler for the usart
                        for char in self.device.getCharacteristics():
                            if char.getHandle() == USART_HANDLER:       
                                self.usart = char

                        self.gui.device_connected()
                        return

                    else:
                        self.gui.update_status('Failed to connect to device')
                        return
            
            self.gui.update_status('Device not found...')

        else:
            self.gui.update_status('Already connected')


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
        self.gui.print(data)
        print(data)


    # Callback from Low Energy device when scanner is active
    def handleDiscovery(self, scan_entry, is_new_dev, is_new_data):
        pass

if __name__ == '__main__':

    ct = Controller()
    ct.connect()
    ct.send('Hey'.encode())