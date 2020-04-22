from pi_anoroc import PiAnoroc

from datetime import datetime
import json
import logging
import os
import screeninfo
import select
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
    'bg': 'black'
}

STYLE_LABEL = {
    'font': 'Times 15',
    'bg': 'black',
    'fg': 'white',
}

STYLE_BUTTONS = {
    'bg': 'black', 
    'fg': 'white',
    'font': 'Times 15',
    'width': '10',
    'height': '1',
    'activebackground': GREEN
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
        self.build_root_window()              # Sets all build variables for the main window
        self.load_images()

        self.pi_anoroc = None                 # Reference to pi_anoroc API
        self.stop_flag = threading.Event()    # Stop flag for synchronizing with pi_anoroc
        self.log_flag  = threading.Event()    # Stop flag for synchronizing with logging monitor

        ## -- Main container for all frames -- ##
        self.frame_main = tk.Frame(self, **STYLE_FRAME)
        self.frame_main.pack_propagate(0)
        self.frame_main.pack(fill='both', expand=True)

        ## -- Navigation frame (TOP) -- ##
        self.frame_nav = self.NavFrame(self.frame_main, self)
        self.frame_nav.pack(fill='x')

        ## -- Center frame (Status & Video) -- ##
        self.frame_center = tk.Frame(self.frame_main, bg='black')
        self.frame_center.pack()

        ## -- Status frame (FPS, Connection etc) -- ##
        self.frame_status = self.StatusFrame(self.frame_center, self)
        self.frame_status.pack(side='left', padx=50)

        ## -- Video frame, here's all the action! -- ##
        self.frame_video = self.VideoFrame(self.frame_center, self)
        self.frame_video.pack(side='right', pady=30)

        ## -- Log frame (Monitors the log file for changes and updates) -- ##
        self.log_frame = self.LogFrame(self.frame_main, self, self.log_flag, **STYLE_FRAME, height=200)
        self.log_frame.pack(fill='x')

        # Initializes the logger
        self._init_logger()



    # Loads all static images and stores them as objects, ready to use for tkinter
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
        self.logo = ImageTk.PhotoImage(Image.open(os.path.join(img_dir, 'anoroc.png')))


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

        self.protocol('WM_DELETE_WINDOW', self._exit)


    # Ensures that all threads are stopped before we close the GUI
    def _exit(self):
        self.log_flag.set()
        self.stop_flag.set()
        self.destroy()

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

    def _connect(self):
        pass
    def _disconnect(self):
        pass


    """
        Container for all the status variables that are read from Anoroc
        All variables are updated with callbacks, and are represented
        as tkinter Vars()
    """
    class StatusFrame(tk.Frame):
        def __init__(self, master, root, **kwargs):
            super().__init__(master, **STYLE_FRAME, **kwargs, height=root._video_height+50, width=400)

            ## -- CONNETION -- ##
            self.label_status = tk.Label(self, text='Status: ', **STYLE_LABEL)
            self.label_status.grid(row=0, column=0, sticky='w')

            self.status_var = tk.StringVar()
            self.status_var.set('Disconnected')

            self.label_status_var = tk.Label(self, textvariable=self.status_var, **STYLE_LABEL)
            self.label_status_var.grid(row=0, column=1, sticky='w', pady=10)


            ## -- BATTERY -- ##

            self.label_battery = tk.Label(self, text='Battery: ', **STYLE_LABEL)
            self.label_battery.grid(row=1, column=0, sticky='w', pady=10)

            self.battery_var = tk.StringVar()
            self.battery_var.set('3.7 V')

            self.label_battery_var = tk.Label(self, textvariable=self.battery_var, **STYLE_LABEL)
            self.label_battery_var.grid(row=1, column=1, sticky='w', pady=10)

            ## -- BATTERY -- ##

            self.fps_status = tk.Label(self, text='FPS: ', **STYLE_LABEL)
            self.fps_status.grid(row=2, column=0, sticky='w', pady=10)

            self.fps_var = tk.IntVar()
            self.fps_var.set(20)

            self.fps_status_var = tk.Label(self, textvariable=self.fps_var, **STYLE_LABEL)
            self.fps_status_var.grid(row=2, column=1, sticky='w', pady=10)


            ## -- MOTOR -- ##
            self.motor_status = tk.Label(self, text='Motors', **STYLE_LABEL)
            self.motor_status.grid(row=3, columnspan=2)
            self.motor_status.config(font = 'Times 20 bold')

            self.motor_canvas = tk.Canvas(self, bd=0, bg='black', width=350)
            self.motor_canvas.grid(row=4, columnspan=2, sticky='w', pady=10, padx=20)

            self.left_motor = self.Motor(self, self.motor_canvas, 50, 100, row=5, col=0, motor='Left')
            self.right_motor = self.Motor(self, self.motor_canvas, 200, 100, row=5, col=1, motor='Right')

            ## -- BUTTONS -- ##

            self.btn_connect = tk.Button(self, text='Connect', command=root._connect, **STYLE_BUTTONS)
            self.btn_connect.grid(row=5, column=0, pady=15)

            self.btn_disconnect = tk.Button(self, text='Disconnect', command=root._disconnect, **STYLE_BUTTONS)
            self.btn_disconnect.grid(row=5, column=1, pady=15)

            # We don't want child widgets to resize the frame
            self.grid_propagate(0)

        """
            A graphical visualization of the motors. Updated by a callback function
        """
        class Motor:

            def __init__(self, frame, canvas, x, y, row, col, motor):

                self.canvas = canvas
                self.frame = frame

                self.width, self.height = 100, 170
                self.y, self.x = y + self.height, x
                self.fill = 0
                
                self.canvas.create_rectangle(x, y, x + self.width, y + self.height, width=4, outline='white')
                self.fill = self.canvas.create_rectangle(x, y, x, y, fill=GREEN)

                self.motor_var = self.canvas.create_text(self.x + (self.width / 2), self.y - (self.height / 2),
                                                         font='Times 20 bold', text='', fill='white')

                self.canvas.create_text(self.x + (self.width / 2), self.y - (self.height / 6),
                                                        font='Times 18 bold', text=motor, fill='white')

                self.update(50)


            def update(self, thrust):

                # Update the Thrust label
                self.canvas.itemconfig(self.motor_var, text='{} %'.format(thrust))
                

                # Convert thrust level do appropiate integer used for adjusting the graphical motor thrust
                thrust = int((thrust / 100) * self.height)

                # Update the graphical motor thrust
                self.canvas.coords(self.fill, self.x + 2, self.y, 
                                    self.x + self.width - 2, self.y - thrust)
                

    class NavFrame(tk.Frame):

        def __init__(self, master, root, **kwargs):
            super().__init__(master, **STYLE_FRAME, height=root._nav_frame_height, **kwargs)
            

            self.master = master
            self.root = root            # Reference to root window

            # The amazing Anoroc logo
            self.logo = tk.Label(self, image=self.root.logo, bd=0)
            self.logo.pack(side='left', padx=(30, 0))

            self.time_var = tk.StringVar()
            self.time_label = tk.Label(self, textvariable=self.time_var, **STYLE_LABEL)
            self.time_label.pack(side='right', padx = (0, 50))

            self.pack_propagate(0)

            self.tick()

        def tick(self):
            self.time_var.set(datetime.now().strftime('%y-%m-%d  %H:%M:%S'))
            self.root.after(1000, self.tick)


    class VideoFrame(tk.Frame):
        """ Container for the camera live-feed """
        def __init__(self, master, root, **kwargs):
            super().__init__(master, width=root._video_width, height=root._video_height+50, **STYLE_FRAME, **kwargs)

            self.root = root    # Reference to root window
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
        def __init__(self, master, root, stop_flag, **kwargs):
            super().__init__(master, **kwargs)

            self.master = master
            self.root = root    # Reference to root window
            self.stop_flag = stop_flag

            self.label_log = tk.Label(self, text='Log', **STYLE_LABEL)
            self.label_log.pack(pady=5)

            self.text = tk.Text(self, **STYLE_LABEL, width=120)
            self.text.pack(side='left', fill='x', padx=10)
            
            self.scroll = tk.Scrollbar(self, width=15)
            self.scroll.pack(side='right', fill='y', padx=10)

            self.text.config(yscrollcommand=self.scroll.set)
            self.scroll.config(command=self.text.yview)
            self.pack_propagate(0)

            # Start monitor the log file             
            threading.Thread(target=self.monitor_log, args=(stop_flag, )).start()

        # Monitors the log file and upates the text field when new data arrives
        def monitor_log(self, stop_flag):
            log_file = os.path.join(self.root.base_dir, self.root.log_file)

            try:
                log = open(log_file)

                while not stop_flag.is_set():
                    line = log.readline()
                    if line:
                        self.text.insert('end', line)
            
            finally:
                log.close()
            


if __name__ == "__main__":

    # Turns off autorepeat behaviour of os (enables detecting keyRelease and keyPress)
    os.system('xset r off')

    gui = Gui()
    gui.set_pi_anoroc(PiAnoroc(gui))
    gui.mainloop()

    # Turn aurorepeat back on
    os.system('xset r on')