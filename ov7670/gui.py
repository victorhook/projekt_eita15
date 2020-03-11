import glob
import os
import sys
from serial import Serial
import tkinter as tk
import tkinter.ttk as ttk

# Constants
BAUD     = 38400
PORT     = '/dev/ttyUSB0'
TIMEOUT  = 0.1
BAUDS    = [9600, 19200, 38400, 57600, 115200]
DATABITS = [5, 6, 7, 8]
STOPBITS = [1, 2]

MEMORY_DEFAULT_HEIGHT = 40

class Register(tk.Entry):

    def __init__(self, addr, name, default, editable, desc=None):
        self.addr     = addr
        self.name     = name
        self.default  = default
        self.desc     = desc if desc else ""
        self.editable = editable
        self.value    = self.default
        self.entry    = None
        self.label    = None

    def __str__(self):
        return '[%s]   %s' % (self.addr, self.name)


REGISTERS = [
    Register('00', 'GAIN', '00', True),
    Register('01', 'BLUE', '80', True),
    Register('02', 'RED', '80', True),
    Register('03', 'VREF', '03', True),
    Register('04', 'COM1', '00', True),
    Register('05', 'BAVE', '00', True),
    Register('06', 'GbAVE', '00', True),
    Register('07', 'AECHH', '00', True),
    Register('08', 'RAVE', '00', True),
    Register('09', 'COM2', '01', True),
    Register('0A', 'PID', '76', False),
    Register('0B', 'VER', '70', False),
    Register('0C', 'COM3', '00', True),
    Register('0D', 'COM4', '40', True),
    Register('0E', 'COM5', '01', True),
    Register('0F', 'COM6', '43', True),

    Register('10', 'AECH', '40', True),
    Register('11', 'CLKRC', '80', True),
    Register('12', 'COM7', '00', True),
    Register('13', 'COM8', '8F', True),
    Register('14', 'COM9', '4A', True),
    Register('15', 'COM10', '00', True),
    Register('16', 'RSVD', 'XX', None),
    Register('17', 'HSTART', '11', True),
    Register('18', 'HSTOP', '61', True),
    Register('19', 'VSTRT', '03', True),
    Register('1A', 'VSTOP', '7B', True),
    Register('1B', 'PSHFT', '00', True),
    Register('1C', 'MIDH', '7F', False),
    Register('1D', 'MIDL', 'A2', False),
    Register('1E', 'MVFP', '00', True),
    Register('1F', 'LAEC', '00', True),

    Register('20', 'ADCCTR0', '04', True),
    Register('21', 'ADCCTR1', '02', True),
    Register('22', 'ADCCTR2', '01', True),
    Register('23', 'ADCCTR3', '80', True),
    Register('24', 'AEW', '75', True),
    Register('25', 'AEB', '63', True),
    Register('26', 'VPT', 'D4', True),
    Register('27', 'BBIAS', '80', True),
    Register('28', 'GbBIAS', '80', True),
    Register('29', 'RSVD', 'XX', None),
    Register('2A', 'EXHCH', '00', True),
    Register('2B', 'EXHCL', '00', True),
    Register('2C', 'RBIAS', '00', True),
    Register('2D', 'ADVFL', '00', True),
    Register('2E', 'ADVFH', '00', True),
    Register('2F', 'YAVE', '00', True),

    Register('30', 'HSYST', '08', True),
    Register('31', 'HSYEN', '30', True),
    Register('32', 'HREF', '80', True),
    Register('33', 'CHLF', '08', True),
    Register('34', 'ARBLM', '03', True),
    Register('35', 'RSVD', 'XX', None),
    Register('36', 'RSVD', 'XX', None),
    Register('37', 'ADC', '04', True),
    Register('38', 'ACOM', '12', True),
    Register('39', 'OFON', '00', True),
    Register('3A', 'TSLB', '0C', True),
    Register('3B', 'COM11', '00', True),
    Register('3C', 'COM12', '40', True),
    Register('3D', 'COM13', '99', True),
    Register('3E', 'COM14', '0E', True),
    Register('3F', 'EDGE', '88', True),

    Register('40', 'COM15', 'C0', True),
    Register('41', 'COM16', '10', True),
    Register('42', 'COM17', '08', True),
    Register('43', 'AWBC1', '14', True),
    Register('44', 'AWBC2', 'F0', True),
    Register('45', 'AWBC3', '45', True),
    Register('46', 'AWBC4', '61', True),
    Register('47', 'AWBC5', '51', True),
    Register('48', 'AWBC6', '79', True),
    Register('49', 'RSVD', 'XX', None),
    Register('4A', 'RSVD', 'XX', None),
    Register('4B', 'REG4B', '00', True),
    Register('4C', 'DNSTH', '00', True),
    Register('4D', 'RSVD', 'XX', None),
    Register('4E', 'RSVD', 'XX', None),
    Register('4F', 'MTX1', '40', True),

    Register('50', 'MTX2', '34', True),
    Register('51', 'MTX3', '0C', True),
    Register('52', 'MTX4', '17', True),
    Register('53', 'MTX5', '29', True),
    Register('54', 'MTX6', '40', True),
    Register('55', 'BRIGHT', '00', True),
    Register('56', 'CONTRAS', '40', True),
    Register('57', 'CONTRAS-CENTER', '80', True),
    Register('58', 'MTXS', '1E', True),
    Register('59', 'RSVD', 'XX', None),
    Register('5A', 'RSVD', 'XX', None),
    Register('5B', 'RSVD', 'XX', None),
    Register('5C', 'RSVD', 'XX', None),
    Register('5D', 'RSVD', 'XX', None),
    Register('5E', 'RSVD', 'XX', None),
    Register('5F', 'RSVD', 'XX', None),

    Register('60', 'RSVD', 'XX', None),
    Register('61', 'RSVD', 'XX', None),
    Register('62', 'LCC1', '00', True),
    Register('63', 'LCC2', '00', True),
    Register('64', 'LCC3', '10', True),
    Register('65', 'LCC4', '80', True),
    Register('66', 'LCC5', '00', True),
    Register('67', 'MANU', '80', True),
    Register('68', 'MANY', '80', True),
    Register('69', 'GFIX', '00', True),
    Register('6A', 'GGAIN', '00', True),
    Register('6B', 'DBLV', '3A', True),
    Register('6C', 'AWBCTR3', '02', True),
    Register('6D', 'AWBCTR2', '55', True),
    Register('6E', 'AWBCTR1', '00', True),
    Register('6F', 'AWBCTR0', '9A', True),

    Register('70', 'SCALING_XSC', '4A', True),
    Register('71', 'SCALING_YSC', '35', True),
    Register('72', 'SCALING_DCWTR', '11', True),
    Register('73', 'SCALING_PCLK_DIV', '00', True),
    Register('74', 'REG74', '00', True),
    Register('75', 'REG75', '0F', True),
    Register('76', 'REG76', '01', True),
    Register('77', 'REG77', '10', True),
    Register('78', 'RSVD', 'XX', None),
    Register('79', 'RSVD', 'XX', None),
    Register('7A', 'SLOP', '24', True),
    Register('7B', 'GAM1', '04', True),
    Register('7C', 'GAM2', '07', True),
    Register('7D', 'GAM3', '10', True),
    Register('7E', 'GAM4', '28', True),
    Register('7F', 'GAM5', '36', True),

    Register('80', 'GAM6', '44', True),
    Register('81', 'GAM7', '52', True),
    Register('82', 'GAM8', '60', True),
    Register('83', 'GAM9', '6C', True),
    Register('84', 'GAM10', '78', True),
    Register('85', 'GAM11', '8C', True),
    Register('86', 'GAM12', '9E', True),
    Register('87', 'GAM13', 'BB', True),
    Register('88', 'GAM14', 'D2', True),
    Register('89', 'GAM15', 'E5', True),
    Register('8A', 'RSVD', 'XX', None),
    Register('8B', 'RSVD', 'XX', None),
    Register('8C', 'RGB444', '00', True),
    Register('8D', 'RSVD', 'XX', None),
    Register('8E', 'RSVD', 'XX', None),
    Register('8F', 'RSVD', '00', None),

    Register('90', 'RSVD', 'XX', None),
    Register('91', 'RSVD', 'XX', None),
    Register('92', 'DM_LNL', '00', True),
    Register('93', 'DM_LNH', '00', True),
    Register('94', 'LCC6', '50', True),
    Register('95', 'LCC7', '50', True),
    Register('96', 'RSVD', 'XX', None),
    Register('97', 'RSVD', 'XX', None),
    Register('98', 'RSVD', 'XX', None),
    Register('99', 'RSVD', 'XX', None),
    Register('9A', 'RSVD', 'XX', None),
    Register('9B', 'RSVD', 'XX', None),
    Register('9C', 'RSVD', 'XX', None),
    Register('9D', 'BD50ST', '99', True),
    Register('9E', 'BD60ST', '7F', True),
    Register('9F', 'HAECC1', 'C0', True),
    
    Register('A0', 'HAECC2', '90', True),
    Register('A1', 'RSVD', 'XX', None),
    Register('A2', 'SCALING_PCLK_DELAY', '02', True),
    Register('A3', 'RSVD', 'XX', None),
    Register('A4', 'NT_CTRL', '00', True),
    Register('A5', 'BD50MAX', '0F', True),
    Register('A6', 'HAECC3', 'F0', True),
    Register('A7', 'HAECC4', 'C1', True),
    Register('A8', 'HAECC5', 'F0', True),
    Register('A9', 'HAECC6', 'C1', True),
    Register('AA', 'HAECC7', '14', True),
    Register('AB', 'BD60MAX', '0F', True),
    Register('AC', 'STR-OPT', '00', True),
    Register('AD', 'STR_R', '80', True),
    Register('AE', 'STR_G', '80', True),
    Register('AF', 'STR_B', '80', True),

    Register('B0', 'ABLC1', '00', True),
    Register('B1', 'RSVD', 'XX', None),
    Register('B2', 'THL_ST', '80', True),
    Register('B3', 'RSVD', 'XX', None),
    Register('B4', 'THL_DLT', '04', True),
    Register('B5', 'RSVD', '1E', None),
    Register('B6', 'RSVD', 'XX', None),
    Register('B7', 'RSVD', 'XX', None),
    Register('B8', 'RSVD', 'XX', None),
    Register('B9', 'RSVD', 'XX', None),
    Register('BA', 'RSVD', 'XX', None),
    Register('BB', 'RSVD', 'XX', None),
    Register('BC', 'RSVD', 'XX', None),
    Register('BD', 'RSVD', 'XX', None),
    Register('BE', 'AD-CHB', '00', True),
    Register('BF', 'AD-CHR', '00', True),

    Register('C0', 'AD-CHGb', '00', True),
    Register('C1', 'AD-CHGr', '00', True),
    Register('C2', 'RSVD', 'XX', None),
    Register('C3', 'RSVD', 'XX', None),
    Register('C4', 'RSVD', 'XX', None),
    Register('C5', 'RSVD', 'XX', None),
    Register('C6', 'RSVD', 'XX', None),
    Register('C7', 'RSVD', 'XX', None),
    Register('C8', 'RSVD', 'XX', None),
    Register('C9', 'SATCTR', 'C0', True),
]

# Return ports availble (Either USB or ACM)
def scan_ports():
    return glob.glob('/dev/tty(USB|ACM)[0-9]*')
        

class OV7670:

    def __init__(self, baud=BAUD, port=PORT, timeout=TIMEOUT):
        self.baud = baud
        self.port = port
        self.timeout = timeout
        self.opened = False
        self.stream = Serial(None, baud, timeout=timeout)

    
    def send(self, command):
        if self.opened:
            self.stream.write(command)

    def __enter__(self):
        self.stream.port = self.port

        if not self.opened:
            try:
                self.stream.open()
                self.opened = True
            except:
                print('Failed to open port %s' % self.port)
                sys.exit(0)


    def __exit(self, *args):
        if self.opened:
            try:
                self.stream.close()
                self.opened = False
            except:
                print('Failed to close port correctly')


class Gui(tk.Tk):

    def __init__(self, camera):
        tk.Tk.__init__(self)

        self.camera = camera

        self.main_frame = tk.Frame(self)
        self.main_frame.pack()

        self.config_frame = self.ConfigFrame(self.main_frame)
        self.config_frame.pack()

        self.communication_frame = self.CommunicationFrame(self.main_frame)
        self.communication_frame.pack(side='left')

        self.memory_area = self.MemoryArea(self.main_frame)
        self.memory_area.pack(side='right')


    class MemoryArea(tk.Canvas):

        def __init__(self, master):
            super().__init__(master)
            
            self.frame = tk.Frame(self)

            self.lbl_reg_name = tk.Label(self, text='Register name')
            self.lbl_value = tk.Label(self, text='Value')

            self.reg_frame = tk.Frame(self)

            self.registers = REGISTERS

            for row, reg in enumerate(self.registers):
                tk.Label(self.reg_frame, text=reg).grid(row=row, column=0, sticky='w')
                entry = tk.Entry(self.reg_frame)
                entry.insert(0, reg.value)
                entry.grid(row=row, column=1)

            self.scroll = tk.Scrollbar(master, orient=tk.VERTICAL, command=self.yview)
            self.configure(yscrollcommand=self.scroll.set)

            self.lbl_reg_name.grid(row=0, column=0)
            self.lbl_value.grid(row=0, column=1)

            self.reg_frame.grid(row=1, columnspan=2)

            self.scroll.pack(side='right', fill='y')
            self.configure(scrollregion=self.bbox('all'))

    class CommunicationFrame(tk.Frame):

        def __init__(self, master):
            super().__init__(master)

            self.send_box = tk.Entry(self)

            self.rcv_box  = tk.Text(self)

            self.send_box.pack()
            self.rcv_box.pack()


    class ConfigFrame(tk.Frame):

        def __init__(self, master):
            super().__init__(master)

            self.master = master

            self.lbl_baud     = tk.Label(self, text='Baud')
            self.lbl_databits = tk.Label(self, text='Data bits')
            self.lbl_stopbit  = tk.Label(self, text='Stop bits')
            self.lbl_ports    = tk.Label(self, text='Port')

            #self.dropdown = ttk.Combobox(self, scan_ports())
            ports = ['/dev/ttyUSB0']
            self.dropdown_ports = ttk.Combobox(self, values=ports, state='readonly')
            self.dropdown_ports.current(0)
           
            self.dropdown_bauds = ttk.Combobox(self, values=BAUDS, state='readonly')
            self.dropdown_bauds.current(0)

            self.dropdown_databits = ttk.Combobox(self, values=DATABITS, state='readonly')
            self.dropdown_databits.current(len(DATABITS) - 1)

            self.dropdown_stopbits = ttk.Combobox(self, values=STOPBITS, state='readonly')
            self.dropdown_stopbits.current(0)
            
                       
            self.lbl_databits.grid(row=0, column=0)
            self.lbl_stopbit.grid(row=1, column=0)
            self.lbl_baud.grid(row=2, column=0)
            self.lbl_ports.grid(row=3, column=0)

            self.dropdown_databits.grid(row=0, column=1)
            self.dropdown_stopbits.grid(row=1, column=1)
            self.dropdown_bauds.grid(row=2, column=1)
            self.dropdown_ports.grid(row=3, column=1)

            self.btn_open = tk.Button(self, text='Open', command=self.open)
            self.btn_open.grid(row=4, columnspan=2)


        def open(self):
            pass



if __name__ == "__main__":
    cam = OV7670()

    gui = Gui(cam)

    gui.mainloop()


    