
from callback import Callback


import bluepy.btle as bt
import struct
import threading
import time

import logging

SCAN_TIMEOUT   = 3
TARGET_MAC     = '50:65:83:0e:9d:5d'
USART_HANDLER  = 37

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

    def __init__(self):

        self.device = None
        self.stream = None
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
        

        self.add_default_callbacks()


    def add_default_callbacks(self):
        self.connected.add_callback(lambda MAC: print('Connected to %s' % MAC))
        #self.disconnected.add_callback(lambda: print('Disconnected'))
        self.connection_failed.add_callback(lambda: print('Connection failed'))
        self.device_not_found.add_callback(lambda: print('Device not found'))
        self.already_connected.add_callback(lambda: print('Already connected to %s' % self.device))


    """ Scans nearby devices and connects to the target if not 
        already connected. Also sets the usart handler to
        send and receive messages (like a socket stream)         """                       
    def connect(self):
        
        if self.device is None:       

            # Scans for nearby devices
            scan = bt.Scanner()
            scan.scan(SCAN_TIMEOUT)

            for dev in scan.getDevices():      # Check if devices match target
                
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
   

    def __enter__(self):
        threading.Thread(target=self.connect).start()
        return self


    def __exit__(self, *args):
        self.stop_flag.set()
        self.disconnect()
        self.send('Exiting!')


    def run(self):

        # Make sure that we're still connected
        if self.device:

            # Enter infinite-loop, running as long as programs wants us to
            while not self.stop_flag.is_set():

                try:
                    self.device.waitForNotifications(1)
                    
                except Exception as e:
                    self.disconnected.call()

        else:
            self.disconnected.call()


    
    # Callback from connected Peripheral
    # c_handle is only needed if multiple devices are used
    def handleNotification(self, c_handle, data):
        try:
            self.packet_received.call(data)
        except Exception as e:
            print(e)



import tkinter as tk

SAMPLE_LIMIT = 10

class Textbox(tk.Frame):

    def __init__(self, master, controller):
        super().__init__(master)

        self.ct = controller

        self.glider = tk.Scale(self, command=self.scale_upd, from_=0, to=64, label="SPEED")
        self.glider.pack()

        self.value = 0

    def ct_callback(self, data):
        value = struct.pack('B', self.value)
        #self.ct.send(value)
        self.ct.send(value)
        print(data)
        

    def scale_upd(self, data):
        self.value = int(data)



def pwm(data):

    value = struct.unpack_from('B', data)[0]
    print(value)


if __name__  == '__main__':
    
    root = tk.Tk()
    root.title('INSANELY FAST BANDVAGN')

    ct = Controller()

    textbox = Textbox(root, ct)
    textbox.grid(row=0, column=0)

    """
    entry = tk.Entry(root, width=40)
    entry.grid(row=0, column=1)

    send = tk.Button(root, width=20, height=10, text='Send')
    send.bind('<Button-1>', lambda data : ct.send(entry.get().encode()))
    send.grid(row=1, columnspan=2)
    """

    connect = tk.Button(root, text='Connect', 
                    command=lambda: threading.Thread(target=ct.connect).start())
    connect.grid(row=2, column=0)

    disconnect = tk.Button(root, text='Disconnect', command=ct.disconnect)
    disconnect.grid(row=2, column=1)

    ct.packet_received.add_callback(textbox.ct_callback)
    
    root.mainloop()

