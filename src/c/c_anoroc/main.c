#include "drivers.h"

int main() {

	init_usart();
	println("init...");
	init_motor_pwm();
	init_adc();
	init_leds();
	init_bluetooth_status_int();

	sei();
	connection_state = disconnected;

	uint8_t pwm_signal = 0;

	while (1) {

		switch (connection_state) {

		case connected:
			PORTC &= ~( (1 << PORTC2) | (1 << PORTC1) | (1 << PORTC0) );
			break;

		case disconnected:

			ADCSRA |= (1 << ADSC);
			while (ADCSRA & (1 << ADSC));
			adjust_pwm(ADCH >> 2);

			/*
			PORTC &= ~(1 << PORTC0);
			PORTC |= 1 << PORTC2;
			_delay_ms(200);
			PORTC &= ~(1 << PORTC2);
			PORTC |= 1 << PORTC1;
			_delay_ms(200);
			PORTC &= ~(1 << PORTC1);
			PORTC |= 1 << PORTC0;
			_delay_ms(200);
			break;
			*/
		}

	}

	return 0;
}
