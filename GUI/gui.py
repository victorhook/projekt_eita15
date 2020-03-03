from controller import Controller
import struct
import threading
from tkinter import *

root = Tk()

# Constants
WIDTH = root.winfo_screenwidth() / 4
HEIGHT = root.winfo_screenheight() / 1.5
MENU_HEIGHT = 100

class CenterFrame(Frame):

    def __init__(self, master, gui, **kwargs):
        super().__init__(master, **kwargs)

        self.gui = gui

        padding = 20
        text_width = 50
        text_height = 10

        frame = Frame(self)

        self.status_text = Label(frame)

        self.btn_connect = Button(frame, text='Connect', command=self._connect)
        self.btn_disconnect = Button(frame, text='Disconnect', command=self._disconnect)
        
        self.label_send = Label(frame, text='Send message')
        self.label_reply = Label(frame, text='Reply')

        self.entry = Entry(frame)
        self.reply = Text(frame, width=text_width, height=text_height)

        self.status_text.grid(row=0, columnspan=2, pady=padding)

        self.btn_connect.grid(row=1, column=0, pady=padding / 2)
        self.btn_disconnect.grid(row=1, column=1, pady=padding / 2)

        self.label_send.grid(row=2, column=0, pady=padding)
        self.label_reply.grid(row=2, column=1, pady=padding)

        self.entry.grid(row=3, column=0, pady=padding)
        self.reply.grid(row=3, column=1, pady=padding)

        self.entry.bind('<Return>', lambda msg: self._send(self.entry.get()))

        small_frame = Frame(frame)
        small_frame.grid(row=4, columnspan=2)

        blue = Button(small_frame, text='TEST!', background='blue',
                    command=lambda: self.gui.send(struct.pack('B', 1 << 0)))
        blue.grid(row=0, column=0)
        red = Button(small_frame, text='RÖD', background='red',
                    command=lambda: self.gui.send(struct.pack('B', 1 << 1)))
        red.grid(row=0, column=1)
        yellow = Button(small_frame, text='GUL', background='yellow',
                    command=lambda: self.gui.send(struct.pack('B', 1 << 3)))
        yellow.grid(row=0, column=2)


        frame.pack()
        self.pack_propagate(0)


    def set_status(self, msg):
        self.status_text['text'] = msg

    """ Callback from buttons / key-presses  """
    def _send(self, msg):
        self.entry.delete(0, 'end')
        self.gui.send(msg.encode())

    def _connect(self):
        self.gui.update_status('Searching for devices...')
        self.gui.connect()

    def _disconnect(self):
        self.gui.disconnect()
        self.gui.update_status('Disconnected')


class Gui:

    def __init__(self, root):

        root.bind('<Destroy>', self.shutdown)

        self.controller = None
        self.com_thread = None

        self.main_frame = Frame(root, width=WIDTH, height=HEIGHT)
        self.main_frame.pack_propagate(0)
        self.main_frame.pack()

        self.top_frame = Frame(self.main_frame, width=WIDTH, height=MENU_HEIGHT, borderwidth=3, relief='groove')
        self.top_frame.grid_propagate(0)
        self.top_frame.pack()

        self.center_frame = CenterFrame(self.main_frame, self, width=WIDTH, height=HEIGHT - MENU_HEIGHT, borderwidth=3, relief='groove')
        self.center_frame.pack()



    """ Callbacks """

    """ Ensures that if there's still a connection,
        it's closed and the thread id killed         """
    def shutdown(self, _):
        try:
            if self.controller:
                self.disconnect()
            if self.com_thread and self.com_thread.is_alive():
                self.controller.kill()

        # Should not enter (debug)
        except Exception as e:
            print(e)

    def device_connected(self):
        self.com_thread = threading.Thread(target=self.controller.run)
        self.com_thread.start()
        
    def send(self, msg):
        print(msg)
        self.controller.send(msg)

    def connect(self):
        if self.controller:
            threading.Thread(target=self.controller.connect).start()

    def disconnect(self):
        self.controller.disconnect()
        

    def set_controller(self, controller):
        self.controller = controller


    def update_status(self, msg):
        self.center_frame.set_status(msg)


    def print(self, msg):
        print(msg)
        self.center_frame.reply.insert(1.0, msg)


gui = Gui(root)
gui.set_controller(Controller(gui))



root.geometry('+%s+%s' % (int(WIDTH / 2), int(HEIGHT / 2) - 200))
root.mainloop()