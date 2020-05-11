#include "drivers.h"

#include <avr/interrupt.h>
#include <avr/portpins.h>
#include <stdint.h>

#define F_CPU 20000000

/** ----- INTERRUPTS ----- **/

// Triggered py PIN Change interrupt (Used for checking connection with Bluetooth module
ISR(PCINT2_vect) {
	if (PINC & (1 << PORTC7)) {
		anoroc->connection = connected;
	} else {
		anoroc->connection = disconnected;
	}
}

// Increments an overflow counter for TIMER 0 (US sensor)
ISR(TIMER0_OVF_vect) {
	if (timer0_overflow == 150) {
		UCSR0A |= (1 << RXC0) | (1 << UDRE0);
	}
	timer0_overflow++;
}

/** ----- Utility functions ----- **/

// Sets the corresponding trigger-pin as output
void init_us_sensor() {
	// Set TRIG pin as OUT
	US_SENSOR_DDR |= (1 << US_SENSOR_TRIG);
	// Set ECHO pin as IN (should be default already)
	US_SENSOR_DDR &= ~(1 << US_SENSOR_ECHO);

	// Enable Overflow Interrupt
	TIMSK0 |= 1 << TOIE0;
}

void init_motor_pwm() {
	/* -- LEFT MOTOR -- */

	// Clear OCX on Compare match, output low
	TCCR1A |= (1 << COM1A1) | (1 << COM1B1);

	// Fast PWM, ICRX as top
	TCCR1A |= (1 << WGM11) | (1 << WGM12);
	TCCR1B |= (1 << WGM13);

	// Prescaler: 8 --> 20MHz => 2.5MHz
	TCCR1B |= 1 << CS11;

	// According do datasheet, typical current control is 50 kHz
	// Top is set as 64 => PWM freq ~= 39kHz
	ICR1 = 64;

	// Setting it to 64 makes it easy to scale, since 256 / 4 = 64
	// which is easly done by shifting 2 bits to the right, eg: INPUT >> 2

	// Sets pins as output
	MOTOR_LEFT_DDR |= (1 << MOTOR_LEFT_PORT1) | (1 << MOTOR_LEFT_PORT2);


	/* -- RIGHT MOTOR --
	 * (Identical to LEFT, but using timer 3, see comments above for details) */
	TCCR3A |= (1 << COM3A1) | (1 << COM3B1);
	TCCR3A |= (1 << WGM31) | (1 << WGM32);
	TCCR3B |= (1 << WGM33);
	TCCR3B |= 1 << CS31;
	ICR3 = 64;
	MOTOR_RIGHT_DDR |= (1 << MOTOR_RIGHT_PORT1) | (1 << MOTOR_RIGHT_PORT2);
}




uint8_t bluetooth_connected() {
	return BLUETOOTH_PIN &= (1 << BLUETOOTH_STATE);
}


void measure_distance() {

	// Reset overflow counter
	timer0_overflow = 0;

	// Send 10 us pulse to start measurement!
	US_SENSOR_PORT |= (1 << US_SENSOR_TRIG);
	_delay_us(10);
	US_SENSOR_PORT &= ~(1 << US_SENSOR_TRIG);

	// Let's wait untill the sensor has sent 8 pulses
	while ( ! (US_SENSOR_PIN & (1 << US_SENSOR_ECHO)) );

	// Pulses are sent from sensor, measurement started, let's start the timer!
	// Prescaler: 1024 --> 256kHz => 78.125kHz
	// Period: 12,8 us
	TCCR0B |= (1 << CS02);
	while ( timer0_overflow < 5 && (US_SENSOR_PIN & (1 << US_SENSOR_ECHO)) );

	// Each timer-overflow takes 3.28 ms, and measures ~ 56.5 cm
	// Stopping at MAX 5 overflows gives us a total range of ~ 2.25m
	// which fits an 8-bit unsigned int in cm

	/* Distance is calulated as:
	 * timer * 12.8 / 58 = X cm
	 * which is roughly ~ timer * 16 / 64 = X cm
	 * which is roughly ~ timer / 4 = timer >> 2
	 */

	// Each timer value is approx ~ 1/4 cm
	uint8_t timer = TCNT0 >> 2;
	// Each overflow is approx ~ 64 cm
	timer += (timer0_overflow << 4);

	// Reset counter and stop the timer, so we're ready for next measurement!
	TCNT0 = 0;
	TCCR0B = 0;

	anoroc->distance = timer;
}



/* Debug function */
void init_adc() {
	// Choosing AREF as voltage reference
	ADMUX |= (1 << REFS0);

	// Left-adjust the ADC result so we get the 8 MSB bits in ADCH
	ADMUX |= (1 << ADLAR);

	// We need 50-200 kHz frequency clock for the ADC
	// System clock = 20 MHz, prescaler = 128
	// ADC frequency = 20MHz/0.128MHz = 156 kHz
	ADCSRA |= (1 << ADPS0) | (1 << ADPS1) | (1 << ADPS2);

	// Enable ADC
	ADCSRA |= (1 << ADEN);

	/* Collecting data: */
	//ADCSRA |= (1 << ADSC);
	//while (ADCSRA & (1 << ADSC));
	//uint8_t data = ADCH;
}

void led_on(uint8_t led, led_color color) {
	switch (led) {
		case LED_LEFT:
			switch (color) {
				case RED:
					LED_LEFT_PORT &= ~( (1 << LED_LEFT_BLUE) | (1 << LED_LEFT_GREEN));
					LED_LEFT_PORT |= 1 << LED_LEFT_RED;
					break;
				case BLUE:
					LED_LEFT_PORT &= ~( (1 << LED_LEFT_RED) | (1 << LED_LEFT_GREEN));
					LED_LEFT_PORT |= 1 << LED_LEFT_BLUE;
					break;
				case GREEN:
					LED_LEFT_PORT &= ~( (1 << LED_LEFT_RED) | (1 << LED_LEFT_BLUE) );
					LED_LEFT_PORT |= 1 << LED_LEFT_GREEN;
					break;
                default:
                    break;
			}
			break;
		case LED_RIGHT:
			switch (color) {
				case RED:
					LED_RIGHT_PORT &= ~( (1 << LED_RIGHT_BLUE) | (1 << LED_RIGHT_GREEN));
					LED_RIGHT_PORT |= 1 << LED_RIGHT_RED;
					break;
				case BLUE:
					LED_RIGHT_PORT &= ~( (1 << LED_RIGHT_RED) | (1 << LED_RIGHT_GREEN));
					LED_RIGHT_PORT |= 1 << LED_RIGHT_BLUE;
					break;
				case GREEN:
					LED_RIGHT_PORT &= ~( (1 << LED_RIGHT_RED) | (1 << LED_RIGHT_BLUE) );
					LED_RIGHT_PORT |= 1 << LED_RIGHT_GREEN;
					break;
				default:
					break;
				}
			break;
		default:
			break;
	}
}


void init_anoroc(anoroc_control *anoroc) {
	anoroc->connection = disconnected;
	anoroc->honk = 0;
	anoroc->distance = 0;
	anoroc->led_left = RED;
	anoroc->led_right = RED;
	anoroc->motor_left = 0;
	anoroc->motor_right = 0;
}

/* Sends all variables to host machine */
void talk_to_host(anoroc_control *anoroc) {
	send_byte((uint8_t) anoroc->distance);
	send_byte((uint8_t) anoroc->led_left);
	send_byte((uint8_t) anoroc->led_right);
	send_byte((uint8_t) anoroc->motor_left);
	send_byte((uint8_t) anoroc->motor_right);
}

/* Adjusts the leds according to anorocs variables */
void led_control() {
	led_on(LED_LEFT, anoroc->led_left);
	led_on(LED_RIGHT, anoroc->led_right);
}

/* Honks if we need are suppose to! */
void honk_control() {
	if (anoroc->honk) {
		HONK_PORT |= 1 << HONK;
	} else {
		HONK_PORT &= ~(1 << HONK);
	}
}

/* Listens to Bluetooth Module, through USART
 * and updates variables Honk status & Motor thrust  */
void listen_to_host() {

	rec_packet * packet;
	read_bytes((uint8_t *) packet, sizeof(packet));
	anoroc->honk = packet->honk;
	anoroc->motor_left = packet->motor_left;
	anoroc->motor_right = packet->motor_right;
}

void steer();

void disconnect() {
	anoroc->connection = disconnected;
	anoroc->led_left = RED;
	anoroc->led_right = RED;
}

void connect() {
	anoroc->connection = connected;
	anoroc->led_left = BLUE;
	anoroc->led_right = BLUE;
}

void init_leds() {
	LED_LEFT_DDR |= (1 << LED_LEFT_RED) | (1 << LED_LEFT_GREEN) | (1 << LED_LEFT_BLUE);
	LED_RIGHT_DDR |= (1 << LED_RIGHT_RED) | (1 << LED_RIGHT_GREEN) | (1 << LED_RIGHT_BLUE);
}
