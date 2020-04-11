from serial import Serial
from tkinter import *
import time

PORT = '/dev/ttyUSB1'
BAUD = 9600




class OV7670:

    def __init__(self, port=PORT, baud=BAUD, timeout=2):
        self.stream = Serial(port, baud, timeout=timeout)

    def write(self, msg):
        self.stream.write(msg)

    def read(self):
        return self.stream.read(0xffffff)

class Pixel:

    def __init__(self, r, g, b):
        self.r = struct.pack('B', int(r))
        self.g = struct.pack('B', int(g))
        self.b = struct.pack('B', int(b))

    def __str__(self):
        return ' |R: %s G: %s B: %s| ' % (round(self.r), round(self.g), round(self.b))

pixels = []
import struct
import cv2
import numpy as np

from PIL import Image

def convert(data):

    r = []
    g = []
    b = []

    for byte in range(len(data[::4])):
        print(ok)
        Cb, Y0, Cr, Y1 = data[byte:byte+4]

        r1 = Y0 + 1.402 * (Cr - 128)
        g1 = Y0 - 0.344136 * (Cb - 128) - 0.71436 * (Cr - 128)
        b1 = Y0 + 1.772 * (Cb - 128)

        r2 = Y1 + 1.402 * (Cr - 128)
        g2 = Y1 - 0.344136 * (Cb - 128) - 0.71436 * (Cr - 128)
        b2 = Y1 + 1.772 * (Cb - 128)

        r.append(r1)
        r.append(r2)
        g.append(g1)
        g.append(g2)
        b.append(b1)
        b.append(b2)

    pixels = list(zip(r, g, b))
    print(pixels)
    return np.array(pixels).reshape(144, 176, 3)

FILE = 'testimg'

def photo():
    s = Serial('/dev/ttyUSB0', 1250000, timeout=2)
    s.write(b'\x03')
    
    # 176*144
    data = s.read(0xfffffff)
    print('[Photo] length of data: %s' % len(data))

    with open(FILE, 'wb') as f:
        f.write(data)
        print('Saving as %s' % FILE)




def ycbcr_to_rbg(data):
    
    xform = np.array([[1, 0, 1.402], [1, -0.34414, -.71414], [1, 1.772, 0]])
    rgb = np.asarray(data).astype(np.float)
    rgb[:,:,[1,2]] -= 128
    rgb = rgb.dot(xform.T)
    np.putmask(rgb, rgb > 255, 255)
    np.putmask(rgb, rgb < 0, 0)
    return np.uint8(rgb)


if __name__ == "__main__":
    
    photo()
    
    with open(FILE, 'rb') as f:
        #data = np.array(list(f.read()))
        data = f.read()

    r = []
    g = []
    b = []

    for byte in range(len(data[::4])):
        
        Cb, Y0, Cr, Y1 = data[byte:byte+4]

        r1 = Y0 + 1.402 * (Cr - 128)
        g1 = Y0 - 0.344136 * (Cb - 128) - 0.71436 * (Cr - 128)
        b1 = Y0 + 1.772 * (Cb - 128)

        r2 = Y1 + 1.402 * (Cr - 128)
        g2 = Y1 - 0.344136 * (Cb - 128) - 0.71436 * (Cr - 128)
        b2 = Y1 + 1.772 * (Cb - 128)
        
        r.extend((r1, r2))
        g.extend((g1, g2))
        b.extend((b1, b2))

    r = np.clip(r, 0, 255)
    g = np.clip(g, 0, 255)
    b = np.clip(b, 0, 255)

    rgb = list(zip(r, g, b))
    data = np.array(rgb)
    
    data = np.reshape(data, (88, 144, 3))
    img = Image.fromarray(data, 'RGB')
    img.save('img.jpg')



    #YCbCr = np.uint8(list(zip(Y, CB, CR)))
    #data = np.array([YCbCr])
    #img = Image.fromarray(data, 'RGB')
    #img.save('img.jpg')




    # data = np.array(pixels).reshape(144, 176, 3)
    # np.array(data).reshape(144, 176)
    """
    data = convert(data)
    
    img = Image.fromarray(data, 'L')
    img.save('test.jpg')
    """
