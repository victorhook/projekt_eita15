import tkinter as tk
import threading
import serial
import struct

def poll(var, s):

    while True:
        try:
            distance = s.read(2)
            if distance:
                distance = struct.unpack('<H', distance)[0]
                distance = int((distance * 13) / 58)
                var.set(distance)
        except:
            pass
            


FONT = 'Courier 30'

s = serial.Serial('/dev/ttyUSB0', 115200, timeout=0)

root = tk.Tk()

frame = tk.Frame(root)
frame.pack()

dist = tk.IntVar()
dist.set(2)


threading.Thread(target=poll, args=(dist, s)).start()


l1 = tk.Label(frame, text='Avstånd: ', font=FONT)
l1.pack(side='left')

l2 = tk.Label(frame, textvariable=dist, font=FONT)
l2.pack(side='right')


root.mainloop()