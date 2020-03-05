#include <avr/io.h>
#include "i2c.h"

#ifndef ADDR_WRITE
#define ADDR_WRITE 0x42
#endif

#ifndef ADDR_READ
#define ADDR_READ 0x43
#endif


#define SEND_START()	        TWCR = (1 << TWEN) | (1 << TWSTA) | (1 << TWINT)
#define SEND_STOP() 	   		TWCR = (1 << TWEN) | (1 << TWSTO) | (1 << TWINT)
#define SEND_DATA() 	   		TWCR = (1 << TWEN) | (1 << TWINT)
#define SEND_DATA_WITH_ACK()	TWCR = (1 << TWEN) | (1 << TWINT) | (1 << TWEA)
#define READ_DATA()		 		TWDR
#define SET_DATA(data)     	    TWDR = data;
#define LOAD_SLA_W()	   		TWDR = (ADDR_WRITE << 1) | 1;
#define LOAD_SLA_R()   			TWDR = ADDR_READ << 1
#define WAIT_FOR_TWINT()    	while (! (TWCR & (1 << TWINT)) )

void init_i2c() {
	TWBR |= 1 << 2;							// Frequency divider
	TWSR |= 1 << 1;							// Prescaler of 4
	PORTC |= (1 << PORTC0) | (1 << PORTC1);	// Pull-ups
}

uint8_t i2c_exchange_byte(uint8_t data) {
	SEND_START();
	WAIT_FOR_TWINT();

	LOAD_SLA_W();
	SEND_DATA();
	WAIT_FOR_TWINT();

	SEND_START();
	WAIT_FOR_TWINT();

	LOAD_SLA_R();
	SEND_DATA();
	WAIT_FOR_TWINT();

	uint8_t tmp;
	tmp = READ_DATA();

	SEND_STOP();
	WAIT_FOR_TWINT();

	return tmp;
}

void i2c_write(uint8_t *data, uint8_t len) {

	SEND_START();
	WAIT_FOR_TWINT();

	LOAD_SLA_W();
	SEND_DATA();
	WAIT_FOR_TWINT();

	for (uint8_t i = 0; i < len; i++) {
		SET_DATA(*data++);
		SEND_DATA();
		WAIT_FOR_TWINT();
	}

	SEND_STOP();
	WAIT_FOR_TWINT();

}
