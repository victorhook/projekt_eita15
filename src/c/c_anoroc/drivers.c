#include "drivers.h"

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

uint8_t measure_battery() {
	// Start conversions!
	ADCSRA |= (1 << ADSC);
	return ADCH;
}

// Sets the corresponding trigger-pin as output
void init_distance_measurement() {
	ULTRA_SENSOR_DDR |= (1 << TRIG_PIN);
}



uint16_t measure_distance() {

	// Send 10 us pulse to start measurement!
	PORTA |= (1 << TRIG_PIN);
	_delay_us(10);
	PORTA &= (0 << TRIG_PIN);

	// Let's wait untill the sensor has sent 8 pulses
	while ( ! (ULTRA_SENSOR_PIN & (1 << ECHO_PIN)) );

	// Pulses are sent from sensor, measurment started, start the timer!
	// Prescaler of 256 => 20MHz -> 78.125kHz
	TCCR1B |= 1 << CS02;
	while ( ULTRA_SENSOR_PIN & (1 << ECHO_PIN) );

	/* Measurement complete!
	 * Duration = 1/f * time-value
	 * Distance is calculated from us/58 = cm
	 * This is handled on the host though, to save run-time on AVR
	 *
	 * 20 MHz / 256 = 78.125 kHz
	 * 1 / 78.125 kHz = 12.8uS period
	 * uS / 58 = centimeters
	 */

	uint16_t timer = TCNT1;

	// Reset counter and stop the timer, so we're ready for next measurement!
	TCNT1 = 0;
	TCCR1B = 0;

	return timer;
}


