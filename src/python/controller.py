
from callback import Callback


import bluepy.btle as bt
import struct
import threading
import time

import logging

SCAN_TIMEOUT   = 2
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
            self.packet_received.call(data, self)
        except Exception as e:
            print(e)





import tkinter as tk

def _connect(controller):
    threading.Thread(target=controller.connect).start()

def _disconnect(controller):
    controller.stop_flag.set()


import struct
RCV_PKT_FORMAT = 'BBBBB'
SND_PKT_FORMAT = 'BBB'

class Anoroc:

    def __init__(self):
                #   T  R  B  L
        self.move = 0

    def _move(self, dir):
        self.move = dir

if __name__ == "__main__":
    ct = Controller()

    ct.stop_flag = threading.Event()

    root = tk.Tk()

    anoroc = Anoroc()
    root.bind('<Key-w>', lambda _: anoroc._move(0))
    root.bind('<Key-d>', lambda _: anoroc._move(1))
    root.bind('<Key-s>', lambda _: anoroc._move(2))
    root.bind('<Key-a>', lambda _: anoroc._move(3))


    frame = tk.Frame(root)
    frame.pack()

    f = tk.Frame(frame, width=300, height=300)
    f.pack()


    connect = tk.Button(root, text='Connect', command=lambda: _connect(ct))
    connect.pack()
    disconnect = tk.Button(root, text='disconnect', command=lambda: ct.stop_flag.set())
    disconnect.pack()

    send = tk.Button(frame, text='send', command=lambda: ct.send(honk = int(textarea.get())))
    send.pack()

    thrust1 = tk.IntVar()
    thrust2 = tk.IntVar()

    scaleframe = tk.Frame(frame)
    scaleframe.pack()

    scale = tk.Scale(scaleframe, from_=-64, to=64, variable=thrust1)
    scale.pack(side='left')
    
    scale = tk.Scale(scaleframe, from_=-64, to=64, variable=thrust2)
    scale.pack(side='right')

    clear = tk.Button(frame, text='clear', command=lambda: textarea.delete('1.0', 'end'))
    clear.pack()




    def respond(data, controller):

        global thrust1, thrust2

        """
        try:
            data = struct.unpack_from(RCV_PKT_FORMAT, data)
        except Exception as e:
            print(e)
        distance, led_left, led_right, motor_left, motor_right = data
        print(f'Distance: {distance}    Led left: {led_left}    Led right: {led_right}    Motor left: {motor_left}     Motor right: {motor_right}')

        packet = struct.pack('BBB', 32, 32, 64)
        controller.send(packet)
        """

        print(struct.unpack_from('BBBBB', data))

        t1, t2 = int(thrust1.get()), int(thrust2.get())

        if t1 < 0:
            t1 = abs(t1) | (1 << 7)

        if t2 < 0:
            t2 = abs(t2) | (1 << 7)

        controller.send(struct.pack('BBB', t1, t2, 0))


    ct.packet_received.add_callback(respond)

    root.mainloop()

