from pi_anoroc import PiAnoroc

import json
import logging
import os
import screeninfo
import time
import tkinter as tk
import tkinter.ttk as ttk
import threading
from PIL import ImageTk, Image

BASE_DIR = os.path.join(os.path.dirname(__file__))
CONFIG_DIR  = 'etc'
CONFIG_FILE = 'anoroc.conf'

GREEN = '#40f900'

STYLE_FRAME = {
    'relief': 'groove',
    'bd': 2,
    'bg': 'white'
}

STYLE_LABEL = {
    'font': 'Times 15',
    'bg': 'white'
}



TMP_CAR = os.path.join(BASE_DIR, CONFIG_DIR, 'car.jpg')


class Gui(tk.Tk):

    """
        The GUI is organized as follows: 
            - 
    """

    def __init__(self):
        
        tk.Tk.__init__(self)

        self.set_configs()                    # Retrieves variables from config file
        self.build_root_window()
        self.load_images()

        self.frame_main = tk.Frame(self, **STYLE_FRAME)
        self.frame_main.pack_propagate(0)
        self.frame_main.pack(fill='both', expand=True)

        self.frame_nav = self.NavFrame(self.frame_main, self)
        self.frame_nav.pack(fill='x')

        self.frame_video = self.VideoFrame(self.frame_main, self)
        self.frame_video.pack(side='right')

        self.frame_sidebar = self.SideFrame(self.frame_main, self)
        self.frame_sidebar.pack(side='left')





        #self._fps = tk.Label(self)
        #self._fps.pack()
        
        #self._btn_connect = tk.Button(self, text='Connect', command=self._cb_connect)
        #self._btn_connect.pack()

        #self._btn_disconnect = tk.Button(self, text='Disconnect', command=self._cb_disconnect)
        #self._btn_disconnect.pack()
        

        #self.log_frame = self.LogFrame(self, background='blue', width=400, height=500)
        #self.log_frame.pack()

        
        self._init_logger()


        self.pi_anoroc = None                 # Reference to pi_anoroc API
        self.stop_flag = threading.Event()    # Stop flag for synchronizing with pi_anoroc

        
    def load_images(self):

        # Base directory for all images
        img_dir = os.path.join(BASE_DIR, 'images')

        # Directory for the control images
        ctrl_dir = os.path.join(img_dir, 'ctrl')                             
        # All the names of the control images
        names = os.listdir(ctrl_dir)
        # Absolute pathways for the control images
        paths = [os.path.join(ctrl_dir, img_name) for img_name in names]
        # Forms a dictionary with "Image name": PhotoImage object
        self.ctrl_imgs = {name.replace('.png', '') : ImageTk.PhotoImage(Image.open(path)) for name, path in zip(names, paths)}


        self.honk_img = ImageTk.PhotoImage(Image.open(os.path.join(img_dir, 'honk.png')))
        self.honk_img_active = ImageTk.PhotoImage(Image.open(os.path.join(img_dir, 'honk_active.png')))
        self.speedometer_img = ImageTk.PhotoImage(Image.open(os.path.join(img_dir, 'speedometer.png')))



    # Sets the geometry and default values for the entire GUI application
    def build_root_window(self):
        
        self.geometry('%sx%s' % (self._width, self._height))
        self.title(self._title)               # Title bar of GUI        

        # Get screen width & height to place the window in the middle of the screen
        monitor = screeninfo.get_monitors()[0]
        x_offset = int((monitor.width - self._width) / 2)
        y_offset = int((monitor.height - self._height) / 2)
        self.geometry('+%s+%s' % (x_offset, y_offset))

        self.minsize(720, 480)

    
    # Opens the config file sets the variables accordingly
    # All configurations are in JSON format
    def set_configs(self):

        self.base_dir = os.path.join(BASE_DIR, CONFIG_DIR)
        if not os.path.exists(self.base_dir):
            os.mkdir(self.base_dir)

        # Build a pathway for the config file
        conf_file = os.path.join(self.base_dir, CONFIG_FILE)

        with open(conf_file) as conf:
            config = json.load(conf)
        
        # Key-bindings for vehicle control
        self.bind('<KeyPress-%s>' % config['forward'], lambda _ : self._mv_forward(True))
        self.bind('<KeyPress-%s>' % config['back'], lambda _ : self._mv_back(True))
        self.bind('<KeyPress-%s>' % config['right'], lambda _ : self._mv_right(True))
        self.bind('<KeyPress-%s>' % config['left'], lambda _ : self._mv_left(True))
        self.bind('<KeyPress-%s>' % config['honk'], lambda _ : self._mv_honk(True))

        self.bind('<KeyRelease-%s>' % config['forward'], lambda _ : self._mv_forward(False), '+')
        self.bind('<KeyRelease-%s>' % config['back'], lambda _ : self._mv_back(False), '+')
        self.bind('<KeyRelease-%s>' % config['right'], lambda _ : self._mv_right(False), '+')
        self.bind('<KeyRelease-%s>' % config['left'], lambda _ : self._mv_left(False), '+')
        self.bind('<KeyRelease-%s>' % config['honk'], lambda _ : self._mv_honk(False), '+')
        

        # Misc GUI settings
        self._title = config['title']
        self._width = int(config['width'])
        self._height = int(config['height'])
        self._video_width = int(config['video_width'])
        self._video_height = int(config['video_height'])
        self._nav_frame_height = int(config['nav_frame_height'])

        # Logging configurations
        self.log_file = config['log_file']
        self.log_mode = config['log_mode']

        self.b1 = False

    def _mv_forward(self, press):
        if press:
            self.keypad.btn_forward['image'] = self.ctrl_imgs['ctrl_forward_green']
        else:
            self.keypad.btn_forward['image'] = self.ctrl_imgs['ctrl_forward_white']

    def _mv_back(self, press):
        if press:
            self.keypad.btn_back['image'] = self.ctrl_imgs['ctrl_back_green']
        else:
            self.keypad.btn_back['image'] = self.ctrl_imgs['ctrl_back_white']

    def _mv_right(self, press):
        if press:
            self.keypad.btn_right['image'] = self.ctrl_imgs['ctrl_right_green']
        else:
            self.keypad.btn_right['image'] = self.ctrl_imgs['ctrl_right_white']

    def _mv_left(self, press):
        if press:
            self.keypad.btn_left['image'] = self.ctrl_imgs['ctrl_left_green']
        else:
            self.keypad.btn_left['image'] = self.ctrl_imgs['ctrl_left_white']

    def _mv_honk(self, press):
        if press:
            self.img_honk['image'] = self.honk_img_active
        else:
            self.img_honk['image'] = self.honk_img


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
        print(self.pi_anoroc)

    # Wrapper for calling update on the VideoFrame object
    def img_update(self, img):
        self.frame_video.img_update(img)

    def fps_update(self, fps):
        self.frame_video.fps.set('FPS: %s' % fps)


    # Initializes a simple logger for information display
    def _init_logger(self):

        self.log = logging.getLogger()
        self.log.setLevel(logging.INFO)

        log_file = os.path.join(self.base_dir, self.log_file)

        handler = logging.FileHandler(log_file, mode=self.log_mode)
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter('[%(asctime)s] %(message)s', '%H:%M:%S'))

        self.log.addHandler(handler)
        self.log.info('New session started')


    class NavFrame(tk.Frame):

        def __init__(self, master, root, **kwargs):
            super().__init__(master, **STYLE_FRAME, height=root._nav_frame_height, **kwargs)
            self.master = master
            self.root = root            # Reference to root window

            self.pack_propagate(0)



    class SideFrame(tk.Frame):
        def __init__(self, master, root, **kwargs):
            super().__init__(master, **STYLE_FRAME, **kwargs)

            self.keypad = self.Keypad(self, root)
            self.keypad.pack()
            root.keypad = self.keypad

            self.img_honk = tk.Label(self, image=root.honk_img)
            self.img_honk.pack()
            root.img_honk = self.img_honk

            self.speedometer = self.SpeedoMeter(self, root)
            self.speedometer.pack()

            self.btn_connect = tk.Button(self, text='Connect', command=root._cb_connect)
            self.btn_connect.pack(side='left')

            self.btn_disconnect = tk.Button(self, text='Disconnect', command=root._cb_connect)
            self.btn_disconnect.pack(side='right')

        class SpeedoMeter(tk.Canvas):

            def __init__(self, master, root):
                super().__init__(master, width=300, height=300)

                self.create_image(150, 150, image=root.speedometer_img)
                self.meter = self.create_line(150, 170, 100, 100, width=5, fill='red')
                
                threading.Thread(target=self.run).start()


            def run(self):

                coords = [ [30 + i*10, 170-i*5] for i in range(12) ]
                coords.extend(coords[::-1])   

                i = 0
                while True:
                    if i == len(coords):
                        i = 0
                    self.coords(self.meter, 150, 170, coords[i][0], coords[i][1])
                    time.sleep(.2)
                    i+=1

                


        class Keypad(tk.Frame):

            def __init__(self, master, root):
                super().__init__(master, **STYLE_FRAME)
                self.root = root
                self.images = root.ctrl_imgs

                self.btn_forward = tk.Label(self, image=self.images['ctrl_forward_white'])
                self.btn_forward.grid(row=0, column=1)

                self.btn_back = tk.Label(self, image=self.images['ctrl_back_white'])
                self.btn_back.grid(row=2, column=1)

                self.btn_right = tk.Label(self, image=self.images['ctrl_right_white'])
                self.btn_right.grid(row=1, column=2)

                self.btn_left = tk.Label(self, image=self.images['ctrl_left_white'])
                self.btn_left.grid(row=1, column=0)


    class VideoFrame(tk.Frame):
        """ Container for the camera live-feed """
        def __init__(self, master, root, **kwargs):
            super().__init__(master, width=root._video_width, height=root._video_height+50, **STYLE_FRAME, **kwargs)

            self.root = root    # Reference to root window
            
            # Frame for displaying info like fps
            self.info_frame = tk.Frame(self, height=50, width=root._video_height, **STYLE_FRAME)
            self.info_frame.pack(side='bottom')
            self.info_frame.pack_propagate(0)

            # FPS variable. The FPS label is automatically updated when the variable changes
            self.fps = tk.StringVar()
            self.fps.set('FPS: ')
            
            # FPS display label
            self._fps = tk.Label(self.info_frame, **STYLE_LABEL, textvariable=self.fps)
            self._fps.pack()



            #tmp_img = Image.open(TMP_CAR).resize((root._video_width, root._video_height))
            #tmp_img = ImageTk.PhotoImage(tmp_img)

            # The image is displayed in a label
            self._image = tk.Label(self, width=root._video_width, height=root._video_height)
            #self._image.image = tmp_img
            self._image.pack()

            self.pack_propagate(0)



        def img_update(self, img):
            # Update the image of the label widget
            self._image.configure(image = img)
            # Tk must keep a reference as well! Otherwise the garbage collector
            # throws it away and the image might not show up
            self._image.image = img

        


    class LogFrame(tk.Frame):
        """ Container for the logging text area """
        def __init__(self, master, **kwargs):
            super().__init__(master, root, **kwargs)
            self.master = master
            self.root = root    # Reference to root window

            self.text = tk.Text(self)
            self.text.pack()



if __name__ == "__main__":

    # Turns off autorepeat behaviour of os (enables detecting keyRelease and keyPress)
    os.system('xset r off')

    gui = Gui()
    gui.set_pi_anoroc(PiAnoroc(gui))
    gui.mainloop()

    # Turn aurorepeat back on
    os.system('xset r on')