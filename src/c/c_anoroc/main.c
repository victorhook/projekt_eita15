#include "drivers.h"
#include "usart.h"

#define POTENTIO_PIN PA0

int main() {

	init_usart();
	init_motor_pwm();
	println("init...");

	uint8_t pwm_value = 0;

	while (1) {

		send_byte(pwm_value);
		pwm_value = read_byte();

		//OCR1A = pwm_value;
		adjust_pwm(pwm_value);
	}

	return 0;
}
