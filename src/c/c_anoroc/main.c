#include <avr/io.h>
#define F_CPU 2000000
#include <util/delay.h>
#include <string.h>
#include "usart.h"

int main() {

	DDRB |= (1 << 1);
	PORTB |= (1 << 1);

	init_usart();
	init_battery_checker();
	println("HEY");

	while (1) {
		print_uint8(battery_measure());
		println(" ");
		_delay_ms(200);
	}

	return 0;
}
