#include "twi.h"
#include "usart.h"

#define DELAY _delay_ms(10)

#define TWI_SREG (TWSR & 0xf8)

/* Write and read address for TWI */
#define ADDR_W 0x42
#define ADDR_R 0x43

enum Error {
	START,
	STOP,
	SEND,
	READ
};

void debug(enum Error error, uint8_t status) {
	send_byte(error);
	send_byte(status);
}

/* All TW status codes are defined in util/twi.h
/* Write/Read address for TWI communication 	  */

void twi_init() {
	TWSR &= ~(1<<TWPS1);
	TWSR &= ~(1<<TWPS0);
	TWBR = 0x40;
}

void twi_start() {
	TWCR = (1 << TWINT) | (1 << TWEN) | (1 << TWSTA);		// Send start condition
	while (! (TWCR & (1 << TWINT)) );						// Wait for ACK
	if (TWI_SREG != TW_START) {
		debug(START, TWI_SREG);
	}
	DELAY;
}

void twi_stop() {
	TWCR = (1 << TWINT) | (1 << TWEN) | (1 << TWSTO);		// Send stop condition
	DELAY;
}

void twi_send(uint8_t data, uint8_t status) {
	TWDR = data;											// Put data in Data register
	TWCR = (1 << TWINT) | (1 << TWEN);						// Send data
	while (! (TWCR & (1 << TWINT)) );						// Wait for ACK
	if (TWI_SREG != status) {
		debug(SEND, TWI_SREG);
	}
	DELAY;
}

uint8_t twi_read_nack() {
	TWCR = (1 << TWINT) | (1 << TWEN);
	while (! (TWCR & (1 << TWINT)) );
	return TWDR;
}

uint8_t twi_read_ack() {
	TWCR = (1 << TWINT) | (1 << TWEN) | (1 << TWEA);
	while (! (TWCR & (1 << TWINT)) );
	return TWDR;
}



uint8_t twi_r_reg(uint8_t addr) {
	twi_start();
	twi_send(ADDR_W, TW_MT_SLA_ACK);
	twi_send(addr, TW_MT_DATA_ACK);
	twi_stop();



	return 0;

}













