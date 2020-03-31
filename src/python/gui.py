import tkinter as tk
import tkinter.ttk as ttk
import threading
from PIL import ImageTk, Image


class Gui(tk.Tk):

    # Callback functions for connect and disconnecting
    def __init__(self):
        tk.Tk.__init__(self)

        self.title('Anoroc')

        self._img_frame = tk.Frame(self, width = 720, height = 480)
        self._img_frame.pack_propagate(0)
        self._img_frame.pack()

        self._image = tk.Label(self._img_frame, width = 720, height = 480)
        self._image.pack()

        self._fps = tk.Label(self)
        self._fps.pack()
        
        self._btn_connect = tk.Button(self, text='Connect', command=self._cb_connect)
        self._btn_connect.pack()

        self._btn_disconnect = tk.Button(self, text='Disconnect', command=self._cb_disconnect)
        self._btn_disconnect.pack()

        self.pi_anoroc = None                   # Reference to pi_anoroc API
        self.stop_flag = threading.Event()      # Stop flag for synchronizing threads


    # Connects to anoroc
    def _cb_connect(self):
        print('Connecting...')
        if self.pi_anoroc:
            self.stop_flag.clear()
            threading.Thread(target=self.pi_anoroc.open, args=(self.stop_flag, )).start()
    

    # Disconnects to anoroc
    def _cb_disconnect(self):
        print('Disconnecting...')
        if self.pi_anoroc:
            self.stop_flag.set()

    # Adds a reference to the network stream
    def set_pi_anoroc(self, pi_anoroc):
        self.pi_anoroc = pi_anoroc

    def img_update(self, img):
        # Update the image of the label widget
        self._image.configure(image = img)
        # Tk must keep a reference as well! Otherwise the garbage collector
        # throws it away and the image might not show up
        self._image.image = img

    def fps_update(self, fps):
        self._fps.configure(text = 'FPS: %s' % fps)






if __name__ == "__main__":

    gui = Gui()
    gui.mainloop()