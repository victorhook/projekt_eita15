from tkinter import *
import threading
from bluepy.btle import *
from bluepy import btle


# Constants
MENU_HEIGHT = 100

TARGET_MAC = '50:65:83:0e:9d:5d'
TIMEOUT = 1

root = Tk()

def print_status(msg):
    status_text['text'] = msg


class RequestHandler(btle.DefaultDelegate):

    def __init__(self):
        super().__init__()

    def handleDiscovery(self, c_handle, data):
        print('c_handle: %s  Data: %s' % (c_handle, data.decode()))

    """ Called when scanner object is active """ 
    def handleNotification(self, scan_entry, data):
        print('Scan entry: %s   Data received: %s' % (scan_entry, data.decode()))


class Connection:

    def __init__(self, scan, gui):

        self.connected = False
        self.connection = None

        self.gui = gui

    def send_msg(self, msg):
        self.write_stuff.write('{}\n'.format(msg).encode())
        self.gui['text'] = ''

    def _connect(self):
        scan.scan(TIMEOUT)
        devices = scan.getDevices()

        for dev in devices:
            
            if (dev.addr.capitalize() == TARGET_MAC):
                print_status('Target detected: %s' % dev.addr)

                if dev.connectable:
                    self.connection = btle.Peripheral(dev)
                    self.connected = True
                    self.connection.setDelegate(RequestHandler())
                    break

                else:
                    print_status('Failed to connect to target...')

        if self.connection is None:
            print_status("Failed to connect to device")
            return
        else:

            characteristics = self.connection.getCharacteristics()

            self.write_stuff = characteristics[-1]
            self.write_stuff.write('Hello World\r\n'.encode(), withResponse=True)

            while True:
                   target=self.connection.waitForNotifications(10)     


    def close(self):
        if (self.connected):
            print("Closing?")
            self.connection.disconnect()
            self.connected = False
            print_status("Connection closed")



scan = btle.Scanner()


def connect_cb():
    print_status('Searching for devices...')    
    threading.Thread(target=connection._connect).start()

def disconnect_cb():
    print("Trying to disconnect")
    connection.close()


width = root.winfo_screenwidth() / 4
height = root.winfo_screenheight() / 1.5

main_frame = Frame(root, width=width, height=height)
main_frame.pack()
main_frame.pack_propagate(0)

menu_frame = Frame(main_frame, width=width, height=MENU_HEIGHT, background='yellow')
menu_frame.pack()

center_frame = Frame(main_frame, width=width, height=height - MENU_HEIGHT, background='green')
center_frame.pack()
center_frame.grid_propagate(0)
center_frame.pack_propagate(0)

btn_connect = Button(center_frame, text='Connect', command=connect_cb)
btn_connect.pack(pady=30)

btn_disconnect = Button(center_frame, text='Disconnect', command=disconnect_cb)
btn_disconnect.pack(pady=30)

label = Label(center_frame, text='INSANE GUI', background='green', font='Arial 50')
label.pack()

status_text = Label(center_frame, background='green')
status_text.pack(pady=20)

entry = Entry(center_frame)
connection = Connection(scan, entry) 
entry.bind('<Return>', lambda msg: connection.send_msg(entry.get()))
entry.pack()


root.geometry('+%s+%s' % (int(width / 2), int(height / 2) - 200))
root.mainloop()
