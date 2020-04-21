#include <avr/io.h>
#include "leds.h"

void init_leds() {
	// Set ports as output
	LED_DDR  |=  (1 << LED_RED) | (1 << LED_GREEN) | (1 << LED_BLUE);
	// Ensure that all leds are off before (shouldn't be needed)
	LED_PORT &= ~( (1 << LED_RED) | (1 << LED_GREEN) | (1 << LED_BLUE) );
}

void init_bluetooth_status_int() {
	// Enable Pin-Change-Interrupt vector 2
	PCICR |= 1 << PCIE2;
	// Enable Pin-Change-Interrupt on pin PC7 (PCINT23)
	PCMSK2 |= 1 << PCINT23;
}
