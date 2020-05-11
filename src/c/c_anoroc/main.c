#include "drivers.h"

int main() {

	init_usart();
	init_us_sensor();
	init_leds();
	init_motor_pwm();
	sei();

	anoroc_control *anoroc;
	init_anoroc(anoroc);

	while (1) {

		switch (anoroc->connection) {
			case connected:
				while (bluetooth_connected()) {
					led_control(anoroc);

					talk_to_host(anoroc);
					anoroc->honk = read_byte();
					anoroc->motor_right = read_byte();
					anoroc->motor_left = read_byte();
					_delay_ms(100);
				}

				disconnect();

				break;

			case disconnected:
				while (!bluetooth_connected()) {
					led_control();
				}
				connect();
				break;
		}

	}

	return 0;
}
