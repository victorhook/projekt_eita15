import socket
import struct
import threading
import time

class HandControl(threading.Thread):

    def __init__(self, ip, port, log=None, anoroc=None):
        super().__init__()
        self.stop_flag = threading.Event()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.ip = ip
        self.port = port

        # Local ip
        self.ip = '192.168.0.7'

        # Anoroc utilities
        self.log = log
        self.anoroc = anoroc


    def run(self):

        self.stop_flag.clear()

        if self.log:
            self.log.info('Listening on port %s at address %s' % (self.port, self.ip))

        try:
            self.sock.bind((self.ip, self.port))
            self.sock.listen(0)

            conn, addr = self.sock.accept()
            if self.log:
                self.log.info('Handcontrol connected to  {}'.format(addr[0]))
            else:
                print('Connected to  {}'.format(addr))

            stream = conn.makefile('rb')
            direction = [False, False, False, False]

            while not self.stop_flag.is_set():

                data = stream.read(struct.calcsize('HH'))

                # Ensure data is not empty
                if data:
                    x, y = struct.unpack('HH', data)
                    if self.anoroc:

                        if y == 0:
                            direction[0] = True
                        else:
                            direction[0] = False

                        if x < 50:
                            direction[1] = True
                        else:
                            direction[1] = False

                        if x > 1000:
                            direction[3] = True
                        else:
                            direction[3] = False                            
                        


                        #motor_thrust_left, motor_thrust_right = self.calc_motor_thrust(x, y)
                        #self.anoroc.motor_left = motor_thrust_left
                        #self.anoroc.motor_right = motor_thrust_right
                        #print(self.anoroc.motor_left, self.anoroc.motor_right)
                        self.anoroc.direction = direction
                    else:
                        print(x, y)
                        

        finally:
            self.sock.close()


    def calc_motor_thrust(self, x, y):
        
        motor_left, motor_right = 0, 0

        if y == 0:
            if x < 50:
                motor_left = 64
                motor_right = 48
            elif x > 1000:
                motor_left = 48
                motor_right = 64
            else:
                motor_left = 64
                motor_right = 64

        else:
            if x < 50:
                motor_left = 64
                motor_right = 0
            elif x > 1000:
                motor_left = 0
                motor_right = 64

        return (motor_left, motor_right)


    def exit(self):
        self.stop_flag.set()
        try:
            self.sock.close()
        except Exception as e:
            if self.log:
                self.log.info('Error when exiting: {}'.format(e))
            else:
                print(e)


if __name__ == "__main__":
    
    handcontrol = HandControl('192.168.0.7', 12000)
    handcontrol.start()

    handcontrol.join()

    HandControl.exit()

    handcontrol.start()