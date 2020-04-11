#include <avr/io.h>

#include "usart.h"

#define F_CPU 1000000
#include <util/delay.h>

int main() {

	init_usart();

	send_byte('a');

	while (1) {
		println("hey!");
		_delay_ms(500);
	}


}
