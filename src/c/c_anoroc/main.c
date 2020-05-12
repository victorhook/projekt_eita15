#include "drivers.h"


int main() {

	init_usart();
	init_us_sensor();
	init_leds();
	init_motor_pwm();
	init_timer0();
	init_honk();
	sei();

	anoroc_control anoroc;
	init_anoroc(&anoroc);

	while (1) {

		switch (anoroc.connection) {
			case connected:
				while (bluetooth_connected()) {
					led_control(&anoroc);
					talk_to_host(&anoroc);
					honk_control(&anoroc);
					measure_distance(&anoroc);

					steer(&anoroc);

					listen_to_host(&anoroc);
					_delay_ms(200);
				}

				disconnect(&anoroc);

				break;

			case disconnected:
				while (!bluetooth_connected()) {
					led_control(&anoroc);
					honk_control(&anoroc);
				}

				connect(&anoroc);
				break;
		}

	}

	return 0;
}
