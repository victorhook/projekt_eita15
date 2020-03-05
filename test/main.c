#include <avr/io.h>
#include "usart.h"

#define F_CPU 8000000
#include <util/delay.h>

static inline void send_start() {
	TWCR = (1 << TWINT) | (1 << TWEN) | (1 << TWSTA);
	send_byte(TWSR);
	while (!(TWCR & (1 << TWINT)) );
	send_byte(TWSR);
}

static inline void send_data(uint8_t data) {
	TWDR = data;
	TWCR = (1 << TWINT) | (1 << TWEN);
	while (!(TWCR & (1 << TWINT)) );
	send_byte(TWSR);
}

static inline void send_stop() {
	TWCR = (1 << TWINT) | (1 << TWEN) | (1 << TWSTO);
	while (!(TWCR & (1 << TWINT)) );
	send_byte(TWSR);
}

static inline uint8_t read_with_ack() {
	TWCR = (1 << TWINT) | (1 << TWEN) | (1 << TWEA);
	while (!(TWCR & (1 << TWINT)) );
	send_byte(TWSR);
	return TWDR;
}

static inline uint8_t read_no_ack() {
	TWCR = (1 << TWINT) | (1 << TWEN);
	while (!(TWCR & (1 << TWINT)) );
	send_byte(TWSR);
	return TWDR;
}

static inline void init_i2c() {
	TWSR = (1 << TWPS1) | (1 << TWPS0) | (1 << TWEN);
}

#define ADDR 0x76

int main() {
	init_usart();
	init_i2c();
	//println("Init...");

	PORTC |= (1 << PORTC0) | (1 << PORTC1);+

	uint8_t data;

	_delay_ms(500);
	send_start();

	while (1) {
		//println("Sending new request!");
		//send_start();

	}

	return 0;
}
