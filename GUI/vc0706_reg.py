REC_PROTO            = 0x56      # 'V'
RET_PROTO            = 0x76      # 'v'

""" Commands """
GEN_VERSION          = 0x11      # Get Firmware version information
SET_SERIAL_NUMBER    = 0x21      # Set serial number
SET_PORT             = 0x24      # Set port
SYSTEM_RESET         = 0x26      # System reset
READ_DATA            = 0x30      # Read data regisvter
WRITE_DATA           = 0x31      # Write data register
READ_FBUF            = 0x32      # Read buffer register
WRITE_FBUF           = 0x33      # Write buffer register
GET_FBUF_LEN         = 0x34      # Get image lengths in frame buffer
SET_FBUF_LEN         = 0x35      # Set image lengths in frame buffer
FBUF_CTRL            = 0x36      # Control frame buffer register
COMM_MOTION_CTRL     = 0x37      # Motion detect on or off in comunication interface
COMM_MOTION_STATUS   = 0x38      # Get motion monitoring status in comunication interface
COMM_MOTION_DETECTED = 0x39      # otion has been detected by comunication interface
MIRROR_CTRL          = 0x3A      # Mirror control
MIRROR_STATUS        = 0x3B      # Mirror status
COLOR_CTRL           = 0x3C      # Control color
COLOR_STATUS         = 0x3D      # Color status
POWER_SAVE_CTRL      = 0x3E      # Power mode control
POWER_SAVE_STATUS    = 0x3F      # Power save mode or not
AE_CTRL              = 0x40      # Control AE
AE_STATUS            = 0x41      # AE status
MOTION_CTRL          = 0x42      # Motion control
MOTION_STATUS        = 0x43      # Get motion status
TV_OUT_CTRL          = 0x44      # TV output on or off control
OSD_ADD_CHAR         = 0x45      # Add characters to OSD channels
DOWNSIZE_CTRL        = 0x54      # Downsize Control
DOWNSIZE_STATUS      = 0x55      # Downsize status
GET_FLASH_SIZE       = 0x60      # Get SPI flash size
ERASE_FLASH_SECTOR   = 0x61      # Erase one block of the flash
ERASE_FLASH_ALL      = 0x62      # Erase the whole flash
READ_LOGO            = 0x70      # Read and show logo
SET_BITMAP           = 0x71      # Bitmap operation
BATCH_WRITE          = 0x80      # Write mass data at a time


""" Status codes """
EXECUTING_COMMAND    = 0         # Executing command right.
SYS_DONT_RECV_CMD    = 1         # System don't receive the command.
DATA_LEN_ERROR       = 2         # The data-length is error.
DATA_FORMAT_ERROR    = 3         # Data format error.
CMD_CANT_EXECUTE     = 4         # The command can not execute now .
CMD_RECV_WRONG_EXE   = 5         # Command received,but executed wrong.
