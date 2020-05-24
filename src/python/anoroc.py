from controller import Controller
import struct

class Anoroc(Controller):

    """
        Representation the Anoroc object.
    """

    def __init__(self, log):

        super().__init__(log)

        # Variables that will control Anoroc
        self.motor_left       = 0
        self.motor_right      = 0
        self.honk             = 0

        # Used improve distance approximation
        self.distance         = 0
        self.distance_counter = 0

        #                   T      R      B      L
        self.direction = [False, False, False, False]

        # Callbacks for sending packet & Timeout
        self.send_packet.add_callback(self.send_data)
        self.timeout.add_callback(self.timeout_cb)

    # Callback from GUI
    def do_honk(self, action):
        if action == 'UP':
            self.honk = 1
        else:
            self.honk = 0

    
    # Callback from GUI
    # Sets the correct direction for Anoroc
    def move(self, direction, action):
        
        if direction == 'FORWARD':
            if action == 'UP':
                self.direction[0] = True
                self.direction[2] = False
            else:
                self.direction[0] = False

        if direction == 'RIGHT':
            if action == 'UP':
                self.direction[1] = True
                self.direction[3] = False
            else:
                self.direction[1] = False
            
        if direction == 'BACK':
            if action == 'UP':
                self.direction[2] = True
                self.direction[0] = False
            else:
                self.direction[2] = False

        if direction == 'LEFT':
            if action == 'UP':
                self.direction[3] = True
                self.direction[1] = False
            else:
                self.direction[3] = False


    # Callback from Bluetooth Controller.
    # This occurs if Anoroc hasn't contacted us in time
    def timeout_cb(self):
        self.log.info('Timeout!')
        self.send_data()


    # Check the direction, calculate motor thrust, then send data
    def send_data(self):
        
        if self.direction[0]:
            # N-E
            if self.direction[1]:
                self.motor_left = 64
                self.motor_right = 48
            # N-W
            elif self.direction[3]:
                self.motor_left = 48
                self.motor_right = 64
            # N
            else:
                self.motor_left = 64
                self.motor_right = 64

        elif self.direction[2]:
            # S-E
            if self.direction[1]:
                self.motor_left = 48
                self.motor_right = 64
            # S-W
            elif self.direction[3]:
                self.motor_left = 64
                self.motor_right = 48
            # S
            else:
                self.motor_left = 64
                self.motor_right = 64

            self.motor_left |= (1 << 7)
            self.motor_right |= (1 << 7)

        else:

            if self.direction[1]:
                self.motor_right = 0
                self.motor_left = 64

            elif self.direction[3]:
                self.motor_right = 64
                self.motor_left = 0

            else:
                self.motor_left = 0
                self.motor_right = 0

        packet = struct.pack('BBB', self.motor_left, self.motor_right, self.honk)
        self.send(packet)