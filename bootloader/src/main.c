#include <avr/io.h>
#include <avr/interrupt.h>
#include "usart.h"
#include "i2c.h"

#define CONNECT_BIN PORTA0
#define CONNECT_PORT PORTA

#define LED_CONNECT_PORT PORTD
#define LED_CONNECT PORTD7

#define BLUE_LED 1 << 0
#define RED_LED 1 << 1
#define YELLOW_LED 1 << 3
#define LEDS_PORT PORTC

#define RESET_TIMER1 TCNT1=TOP
#define TOP UINT16_MAX-3906

volatile uint8_t connected;

ISR(PCINT0_vect) {
	if (!connected) {
		connected = 1;
		//println("Welcome!");
	} else {
		connected = 0;
	}
}

ISR(TIMER1_OVF_vect) {
	if (connected) {
		LED_CONNECT_PORT ^= 1 << LED_CONNECT;
	}
	RESET_TIMER1;
}


ISR(USART0_RX_vect) {
	uint8_t data = UDR0;
	if (data == 1) {

		//send_byte(data);

		// Start
		TWCR = (1 << TWINT) | (1 << TWSTA) | (1 << TWEN);
		while (! (TWCR & (1 << TWINT)) );

		// SLA_W
		TWDR = 0x42 << 1;
		TWCR |= (1 << TWINT) | (1 << TWEN);
		while (! (TWCR & (1 << TWINT)) );

		// Send register addr
		TWDR = 0x0A;
		TWCR |= (1 << TWINT) | (1 << TWEN);
		while (! (TWCR & (1 << TWINT)) );

		// Restart
		TWCR = (1 << TWINT) | (1 << TWSTA) | (1 << TWEN);
		while (! (TWCR & (1 << TWINT)) );

		// SLA_R
		TWDR = (0x43 << 1) | 1;
		TWCR |= (1 << TWINT) | (1 << TWEN);
		while (! (TWCR & (1 << TWINT)) );

		// Data received
		TWCR = (1 << TWINT) | (1 << TWEN);
		while (! (TWCR & (1 << TWINT)) );

		data = TWDR;
		uint8_t status = TWSR;

		// Stop
		TWCR |= (1 << TWINT) | (1 << TWEN) | (1 << TWSTO);

		send_byte(status);
		send_byte(data);
	}
}

void init_timers() {
	// CLock prescaler
	TCCR1B |= (1 << CS12) | (1 << CS10);

	// Enable interrupt on overflow
	TIMSK1 |= 1 << TOIE1;

	// Set start value (2 Hz)
	RESET_TIMER1;
}

void init_pc_connect() {
	PCICR |= 1 << PCIE0;
	PCMSK0 |= 1 << CONNECT_BIN;
}

int main() {

	init_usart();
	// Enable RX interrupt for USART
	UCSR0B |= 1 << RXCIE0;

	init_i2c();
	init_pc_connect();
	init_timers();
	sei();

	println("Init");

	DDRD |= 1 << 7;
	connected = 0;

	while(1) {
		if (!connected) {
			LED_CONNECT_PORT &= 0 << LED_CONNECT;
		}
	}

	return 0;
}
