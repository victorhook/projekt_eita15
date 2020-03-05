from bluepy.btle import *
import threading
import time

class RequestHandler(DefaultDelegate):

    def __init__(self):
        super().__init__()

    def handleDiscovery(self, c_handle, data):
        print('c_handle: %s  Data: %s' % (c_handle, data.decode()))

    """ Called when scanner object is active """ 
    def handleNotification(self, scan_entry, data):
        print('Scan entry: %s   Data received: %s' % (scan_entry, data.decode()))


TARGET_MAC = '50:65:83:0e:9d:5d'
0
scan = Scanner()
scan.scan(1)

devices = scan.getDevices()

for dev in devices:
    
    if (dev.addr.capitalize() == TARGET_MAC):
        print("Target detected: %s" % dev.addr)

        if dev.connectable:
            connection = Peripheral(dev)
            connection.setDelegate(RequestHandler())

            characteristics = connection.getCharacteristics()

            write_stuff = characteristics[-1]
            write_stuff.write('Hello World\r\n'.encode(), withResponse=True)

            while True:
                connection.waitForNotifications(10)