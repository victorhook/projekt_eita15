typedef unsigned char uint8_t;

#define REC_PROTO 0x56  // 'V'
#define RET_PROTO 0x76  // 'v'


/*
Status code Error instructions
0 Executing command right.
1 System don't receive the command.
2 The data-length is error.
3 Data format error.
4 The command can not execute now .
5 Command received,but executed wrong
*/

// Commands
#define GEN_VERSION 0x11            // Get Firmware version information
#define SET_SERIAL_NUMBER 0x21      // Set serial number
#define SET_PORT 0x24               // Set port
#define SYSTEM_RESET 0x26           // System reset
#define READ_DATA 0x30              // Read data regisvter
#define WRITE_DATA 0x31             // Write data register
#define READ_FBUF 0x32              // Read buffer register
#define WRITE_FBUF 0x33             // Write buffer register
#define GET_FBUF_LEN 0x34           // Get image lengths in frame buffer
#define SET_FBUF_LEN 0x35           // Set image lengths in frame buffer
#define FBUF_CTRL 0x36              // Control frame buffer register
#define COMM_MOTION_CTRL 0x37       // Motion detect on or off in comunication interface
#define COMM_MOTION_STATUS 0x38     // Get motion monitoring status in comunication interface
#define COMM_MOTION_DETECTED 0x39   //Motion has been detected by comunication interface
#define MIRROR_CTRL 0x3A            // Mirror control
#define MIRROR_STATUS 0x3B          // Mirror status
#define COLOR_CTRL 0x3C             // Control color
#define COLOR_STATUS 0x3D           // Color status
#define POWER_SAVE_CTRL 0x3E        // Power mode control
#define POWER_SAVE_STATUS 0x3F      // Power save mode or not
#define AE_CTRL 0x40                // Control AE
#define AE_STATUS 0x41              // AE status
#define MOTION_CTRL 0x42            // Motion control
#define MOTION_STATUS 0x43          // Get motion status
#define TV_OUT_CTRL 0x44            // TV output on or off control
#define OSD_ADD_CHAR 0x45           // Add characters to OSD channels
#define DOWNSIZE_CTRL 0x54          // Downsize Control
#define DOWNSIZE_STATUS 0x55        // Downsize status
#define GET_FLASH_SIZE 0x60         // Get SPI flash size
#define ERASE_FLASH_SECTOR 0x61     // Erase one block of the flash
#define ERASE_FLASH_ALL 0x62        // Erase the whole flash
#define READ_LOGO 0x70              // Read and show logo
#define SET_BITMAP 0x71             // Bitmap operation
#define BATCH_WRITE 0x80            // Write mass data at a time

#define BAUD_SIZE 4


void * alloc(uint8_t);

void set_baud(unsigned long baud) {
    rec_cmd packet;
    packet.proto = REC_PROTO;
    packet.serial_nbr = 0;
    packet.command = SET_PORT;
    packet.data_len = BAUD_SIZE;
    *packet.data = baud;
}


typedef struct {
    uint8_t proto;         
    uint8_t serial_nbr;    
    uint8_t command;       
    uint8_t data_len;       
    uint8_t data[16];          // 0-16 Bytes
} rec_cmd;

typedef struct {
    uint8_t proto;
    uint8_t serial_nbr;
    uint8_t command;
    uint8_t status;         // Shows whether the command is OK
    uint8_t data_len;
    uint8_t data[16];          // 0-16 Bytes
} retun_cmd;