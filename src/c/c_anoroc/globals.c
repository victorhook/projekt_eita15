enum {
	connected,
	disconnected
} connection_state;

enum {
	RED,
	GREEN,
	BLUE
} connection_leds;

typedef enum {
	FORWARD,
	BACKWARDS,
	RIGHT,
	LEFT
} direction ;


/* Packet structure for RECEIVING
 * <---------- bits ------------->
 * |		     |    0     |   1-7  |
 * | Left motor  | Reverse  | Thrust |
 * |             |    8     |   9-15 |
 * | Right motor | Reverse  | Thrust |
 * |   			 |    16    | 17-23  |
 * | 			 |   Honk   | Unused |   
*/

typedef struct {
	uint8_t motor_left,
	uint8_t motor_right,
	uint8_t honk,
} rec_packet;


/* Packet structure for RECEIVING
 * <---------- bits ------------->
 * |		     |    0     |   1-7  |
 * | Left motor  | Reverse  | Thrust |
 * |        8-15 |
 * | Battery Voltage | 
 * |        15-23 |
 * | Distance to front |
 * | 			 |   Honk   | Unused |   
*/

typedef struct {
	uint8_t state,
	uint8_t battery_level,
	uint8_t distance,
} send_packet;
