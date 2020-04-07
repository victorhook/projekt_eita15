#include "drivers.h"
#include "usart.h"


int main() {

	DDRB |= (1 << 1);
	PORTB |= (1 << 1);

	init_usart();
	//init_battery_checker();
	init_distance_measurement();

	println("HEY");

	while (1) {
		uint16_t distance = measure_distance();
		send_byte(distance & 0x00ff);
		send_byte(distance >> 8);
		_delay_ms(100);
	}

	return 0;
}
