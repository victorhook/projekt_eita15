#include <avr/io.h>
#include "i2c.h"

void init_i2c() {
	// Set bit rate
	TWBR |= 1 << 5;

	// Enable TWI
	TWCR |= TWEN;

	// Set DDR
	I2C_DDR |= (1 << SCL_PIN) | (1 << SDA_PIN);
}

void i2c_wait_for_complete() {
	while (! (TWCR & (1 << TWINT)) );
}

void i2c_start() {
	TWCR = (1 << TWSTA) | (1 << TWINT) | (1 << TWEN);
	i2c_wait_for_complete();
}

void i2c_stop() {
	TWCR = (1 << TWINT) | (1 << TWEN) | (1 << TWSTO);
}

uint8_t i2c_read_ack() {
	TWCR = (1 << TWINT) | (1 << TWEN) | (1 << TWEA);
	i2c_wait_for_complete();
	return TWDR;
}

uint8_t i2c_read_no_ack() {
	TWCR = (1 << TWINT) | (1 << TWEN);
	i2c_wait_for_complete();
	return TWDR;
}

void i2c_send(uint8_t data) {
	TWDR = data;
	TWCR = (1 << TWINT) | (1 << TWEN);
	i2c_wait_for_complete();
}
