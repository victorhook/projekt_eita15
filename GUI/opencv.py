import cv2
import numpy as np
import time
import threading
from tkinter import *
import os
from PIL import Image, ImageTk
from vc0706 import VC0706

img_path = os.path.join(os.path.dirname(__file__), 'images/images0.jpg')
prog_running = True

def sample_camera():
    camera = VC0706()
    camera.enable_save()
    camera.connect()
    
    while prog_running:
        print('Snap!')
        camera.photo()



class GUI:

    def __init__(self, root):

        self.root = root

        self.frame = Frame(self.root, width=400, height=400)
        self.frame.pack()

        self.image = Label(self.frame, image=None)
        self.image.pack()

        self.update()

    def update(self):
        print('Updating!')
        img = ImageTk.PhotoImage(Image.open(img_path))
        self.image.configure(image=img)
        self.image.image = img
        self.root.after(1000, self.update)
        

if __name__ == "__main__":

    threading.Thread(target=sample_camera).start()

    root = Tk() 
    
    gui = GUI(root)

    root.mainloop()
