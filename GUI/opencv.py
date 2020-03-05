import cv2
import numpy as np
import time
import threading
from tkinter import *
import os
from PIL import Image, ImageTk
from vc0706 import VC0706

img_path = None
prog_running = True

def sample_camera(camera, gui):
    
    camera.enable_save()
    camera.connect()
    
    while prog_running:
        t1 = time.time()
        camera.photo()
        gui.update(time.time() - t1)

class GUI:

    def __init__(self, root, camera):

        self.root = root

        self.frame = Frame(self.root, width=400, height=400)
        self.frame.pack()

        self.fps = Label(self.frame)
        self.fps.pack()

        self.image = Label(self.frame, image=None)
        self.image.pack()
        self.image_path = camera.get_image_path()

        self.update(1)

    def update(self, delay):
        self.fps['text'] = 'FPS %s' % round(1 / delay, 3)
        img = ImageTk.PhotoImage(Image.open(self.image_path))
        self.image.configure(image=img)
        self.image.image = img
        #self.root.after(1000, self.update)
        

if __name__ == "__main__":

    root = Tk() 

    camera = VC0706()
    gui = GUI(root, camera)

    threading.Thread(target=sample_camera, args=(camera, gui)).start()


    root.mainloop()
