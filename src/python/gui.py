import json
import logging
import tkinter as tk
import tkinter.ttk as ttk
import threading
from PIL import ImageTk, Image

CONFIG_FILE = 'anoroc.conf'

class Gui(tk.Tk):

    """
        The GUI is organized as follows: 
            - 
    """

    def __init__(self):
        tk.Tk.__init__(self)
        
        self.set_configs()                    # Retrieves variables from config file
        self.pi_anoroc = None                 # Reference to pi_anoroc API
        self.stop_flag = threading.Event()    # Stop flag for synchronizing threads


        self.title(self._title)               # Title bar of GUI

        self.center_frame = tk.Frame(self, width = self._width, height = self._height, background='red')
        self.center_frame.pack()

        self.video_frame = self.VideoFrame(self.center_frame, width=720, height=self._video_height,
                                background='blue')
        self.video_frame.pack()

        #self._fps = tk.Label(self)
        #self._fps.pack()
        
        self._btn_connect = tk.Button(self, text='Connect', command=self._cb_connect)
        self._btn_connect.pack()

        self._btn_disconnect = tk.Button(self, text='Disconnect', command=self._cb_disconnect)
        self._btn_disconnect.pack()
        

        #self.log_frame = self.LogFrame(self, background='blue', width=400, height=500)
        #self.log_frame.pack()

        
        self._init_logger()


    # Opens the config file sets the variables accordingly
    # All configurations are in JSON format
    def set_configs(self):
        with open(CONFIG_FILE) as conf:
            config = json.load(conf)
        
        # Key-bindings for vehicle control
        self.bind('<Key-%s>' % config['forward'], self._mv_forward)
        self.bind('<Key-%s>' % config['back'], self._mv_back)
        self.bind('<Key-%s>' % config['right'], self._mv_right)
        self.bind('<Key-%s>' % config['left'], self._mv_left)
        self.bind('<Key-%s>' % config['honk'], self._mv_honk)

        # Misc GUI settings
        self._title = config['title']
        self._width = config['width']
        self._height = config['height']
        self._video_width = config['video_width']
        self._video_height = config['video_height']

        # Logging configurations
        self.log_output = config['log_output']
        self.log_mode = config['log_mode']


    def _mv_forward(self, _):
        print('Forward!')

    def _mv_back(self, _):
        print('Back!')

    def _mv_right(self, _):
        print('Right!')

    def _mv_left(self, _):
        print('Left!')

    def _mv_honk(self, _):
        print('Honk!')


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

    # Wrapper for calling update on the VideoFrame object
    def img_update(self, img):
        self.video_frame.img_update(img)

    def fps_update(self, fps):
        self._fps.configure(text = 'FPS: %s' % fps)


    # Initializes a simple logger for information display
    def _init_logger(self):
        self.log = logging.getLogger()
        self.log.setLevel(logging.INFO)

        handler = logging.FileHandler(self.log_output, mode=self.log_mode)
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter('[%(asctime)s] %(message)s', '%H:%M:%S'))

        self.log.addHandler(handler)
        self.log.info('New session started')


    class VideoFrame(tk.Frame):
        """ Container for the camera live-feed """
        def __init__(self, master, width, height, **kwargs):
            super().__init__(master, **kwargs)

            self._image = tk.Label(self, width = width, height = height)
            self._image.pack()

            self._fps = tk.Label(self)
            self._fps.pack()

        def img_update(self, img):
            # Update the image of the label widget
            self._image.configure(image = img)
            # Tk must keep a reference as well! Otherwise the garbage collector
            # throws it away and the image might not show up
            self._image.image = img

        


    class LogFrame(tk.Frame):
        """ Container for the logging text area """
        def __init__(self, master, **kwargs):
            super().__init__(master, **kwargs)
            self.master = master

            self.text = tk.Text(self)
            self.text.pack()



if __name__ == "__main__":

    gui = Gui()
    gui.mainloop()

