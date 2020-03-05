#include <avr/io.h>
#include <avr/interrupt.h>
#define F_CPU 8000000
#include "usart.h"

#include <util/delay.h>

#define btn_pressed() !(PINB & (1 << PINB1))
#define BLINK_TOP 0xffff - 3908

#define BTNS_PORT PORTB
#define BTNS_DDR DDRB
#define BLUE_BTN PORTB2
#define GREEN_BTN PORTB0

typedef enum {
	BOOTLOADER,
	NORMAL,
} mode;


volatile mode state;

ISR(PCINT1_vect) {

	if (btn_pressed()) {
		state = state == NORMAL ? BOOTLOADER : NORMAL;
	}
}

ISR(TIMER1_OVF_vect) {
	if (state == BOOTLOADER) {
		BTNS_PORT ^= 1 << BLUE_BTN;
	} else {
		BTNS_PORT ^= 1 << GREEN_BTN;
	}
	TCNT1 = BLINK_TOP;
}

void init_btn() {
	PCICR |= 1 << PCIE1;					// Choose pin group
	PCMSK1 |= 1 << PCINT9;					// Mask correct pin
}

void init_blink_timer() {
	TCCR1B |= (1 << CS10) | (1 << CS12);	// Set prescaler
	TIMSK1 |= 1 << TOIE1;					// Enable interrupt on overflow
	TCNT1 = BLINK_TOP;						// Set counter to correct value for 2 Hz
}

int main() {

	init_usart();
	init_btn();
	init_blink_timer();
	sei();

	state = NORMAL;

	println("Init...");
	println("Starting up in normal mode...");

	PORTB |= 1 << PORTB1;
	BTNS_DDR |= (1 << BLUE_BTN) | (GREEN_BTN);		// Internal pull-ups

	while (1) {

	}

	return 0;
}
