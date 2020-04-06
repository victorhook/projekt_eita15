#include <avr/io.h>
#include "anoroc_utils.h"


// We're using pin PA0 (ADC0) as input
void init_battery_checker() {
	// Choosing AREF as voltage reference
	ADMUX |= (1 << REFS0);

	// Left-adjust the ADC result so we get the 8 MSB bits in ADCH
	ADMUX |= (1 << ADLAR);

	// We need 50-200 kHz frequency clock for the ADC
	// System clock = 20 MHz, prescaler = 128
	// ADC frequency = 20MHz /0.128MHz = 156 kHz
	ADCSRA |= (1 << ADPS0) | (1 << ADPS1) | (1 << ADPS2);

	// Enable ADC
	ADCSRA |= (1 << ADEN);

	// Free running mode, let's start conversions!
	//ADCSRA |= (1 << ADSC);
}

uint8_t battery_measure() {
	// Start conversions!
	ADCSRA |= (1 << ADSC);
	return ADCH;
}
