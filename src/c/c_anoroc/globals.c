#include <avr/io.h>

/* --- PIN DEFINITIONS --. */

#define LED_LEFT 0
#define LED_RIGHT 1

#define LED_LEFT_DDR DDRA
#define LED_LEFT_PORT PORTA
#define LED_LEFT_RED PA3
#define LED_LEFT_GREEN PA2
#define LED_LEFT_BLUE PA1

#define LED_RIGHT_DDR DDRC
#define LED_RIGHT_PORT PORTC
#define LED_RIGHT_RED PC1
#define LED_RIGHT_GREEN PC3
#define LED_RIGHT_BLUE PC2

#define HONK_DDR DDRB
#define HONK_PORT PORTB
#define HONK PB2

#define US_SENSOR_PIN PINA
#define US_SENSOR_DDR DDRA
#define US_SENSOR_PORT PORTA
#define US_SENSOR_TRIG PA6
#define US_SENSOR_ECHO PA7

#define BLUETOOTH_PIN PIND
#define BLUETOOTH_RX PD0
#define BLUETOOTH_TX PD1
#define BLUETOOTH_STATE PD2

#define MOTOR_LEFT_DDR DDRD
#define MOTOR_LEFT_PORT1 PD4
#define MOTOR_LEFT_PORT2 PD5

#define MOTOR_RIGHT_DDR DDRB
#define MOTOR_RIGHT_PORT1 PB6
#define MOTOR_RIGHT_PORT2 PB7

#define START_MESSAGE 0xff
#define END_MESSAGE 0xfe


/* --- Global variables --- */
uint8_t timer0_overflow;


/* --- ENUMS & TYPES --- */

typedef enum {
	connected,
	disconnected
} connection_state;

typedef enum {
	RED,
	GREEN,
	BLUE,
} led_color ;

typedef enum {
	FORWARD,
	BACKWARDS,
	RIGHT,
	LEFT
} direction ;


typedef struct {
	uint8_t motor_left;
	uint8_t motor_right;
	uint8_t honk;
	uint8_t distance;
	led_color led_left;
	led_color led_right;
	connection_state connection;
} anoroc_control ;

anoroc_control *anoroc;

/* Packet structure for RECEIVING
 * <---------- bits ------------->
 * | >> BITS >>> |    0     |   1-6  |    7   |
 * | Left motor  | Reverse  | Thrust | Unused |
 * | >> BITS >>> |    8     |   9-14 |   15   |
 * | Right motor | Reverse  | Thrust | Unused |
 * | >> BITS >>> |    16    |      17-23      |
 * | Honk & misc |   Honk   |     Unused      |
*/

typedef struct {
	uint8_t motor_left;
	uint8_t motor_right;
	uint8_t honk;
} rec_packet ;


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
