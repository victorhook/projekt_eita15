#include <avr/io.h>
#include <avr/interrupt.h>
#include <avr/wdt.h>

#define BAUD 115200

#include "usart.h"
#include <util/twi.h>

#ifndef F_CPU
#define F_CPU 8000000
#endif

/* JTAG fuses must be disabled for these pins */
#define VSYNC      PORTC4
#define HREF       PORTC5
#define PCLK       PORTC6

#define CAMERA_PIN PINA

#define TWI_DELAY 50

#include <util/delay.h>

#define ENABLE_RX_INTERRUPT UCSR0B |= 1 << RXCIE0

 /* All TW status codes are defined in util/twi.h
 /* Write/Read address for TWI communication 	  */
#define ADDR_W 0x42
#define ADDR_R 0x43


void sample();


void debug_err(uint8_t func_id) {
	send_byte(0xDD);
	send_byte(func_id);
	send_byte(TWSR & 0xf8);
}

void twi_start() {
	TWCR = (1 << TWINT) | (1 << TWSTA) | (1 << TWEN);
	while (! (TWCR & (1 << TWINT)) );
	if ((TWSR & 0xf8) != TW_START) {
		debug_err(0x01);
	}
}

void twi_send(uint8_t data, uint8_t status) {
	TWDR = data;
	TWCR = (1 << TWINT) | (1 << TWEN);
	while (! (TWCR & (1 << TWINT)) );
	if ( (TWSR & 0xf8) != status ) {
		debug_err(0x02);
	}
}

uint8_t twi_read_nack() {
	TWCR = (1 << TWINT) | (1 << TWEN);
	while (! (TWCR & (1 << TWINT)) );

	if ( (TWSR & 0xf8) != TW_MR_DATA_NACK ) {
		debug_err(0x03);
	}
	return TWDR;
}

uint8_t twi_read_ack() {
	TWCR = (1 << TWINT) | (1 << TWEN);
	while (! (TWCR & (1 << TWINT)) );

	if ( (TWSR & 0xf8) != TW_MR_DATA_ACK ) {
		debug_err(0x03);
	}
	return TWDR;
}

void init_twi() {
	TWSR = 1 << TWPS1;
	TWBR = 1;
}

void twi_stop() {
	TWCR = (1 << TWINT) | (1 << TWEN) | (1 << TWSTO);
}

void twi_w_reg(uint8_t addr, uint8_t data) {
	twi_start();						// Start transmission
	twi_send(ADDR_W, TW_MT_SLA_ACK);	// Send address, enter Master Transmitter mode
	twi_send(addr, TW_MT_DATA_ACK);		// Select register to write to
	twi_send(data, TW_MT_DATA_ACK);		// What data to write
	twi_stop();							// Stop transmission
	_delay_us(TWI_DELAY);		// NEEDED
}

uint8_t twi_r_reg(uint8_t addr) {

	twi_start();						// Start transmission
	twi_send(ADDR_W, TW_MT_SLA_ACK);	// Send address, enter Master Transmitter mode
	twi_send(addr, TW_MT_DATA_ACK);		// Select register to read
	twi_stop();							// OV7670 doesn't support restart, need to stop twi
	_delay_us(TWI_DELAY);		// NEEDED

	twi_start();						// Start new transmission
	twi_send(ADDR_R, TW_MR_SLA_ACK);	// Send address, enter Master Receiver mode
	uint8_t data = twi_read_nack();		// Read data, send nack to confirm no more data needed
	twi_stop();							// Stop transmission
	_delay_us(TWI_DELAY);		// NEEDED

	return data;
}

void twi_reset() {
	twi_w_reg(0x12, 0x80);
	_delay_ms(1);
}
void check_lines();
void check_cols();


ISR(USART0_RX_vect) {
	uint8_t command = UDR0, reg_addr, data;
	//uint8_t pixels[8];

	switch (command) {
	case 0x00:
		reg_addr = read_byte();
		send_byte(twi_r_reg(reg_addr));
		break;
	case 0x01:
		reg_addr = read_byte();
		data = read_byte();
		twi_w_reg(reg_addr, data);
		send_byte(0x69);
		break;
	case 0x03:
		sample();
		break;
	case 0x04:
		twi_reset();
		break;
	case 0x05:
		check_cols();
		break;
	case 0x06:
		check_lines();
		break;
	case 0x07:
		sample();
		break;
	}
}

#define HREF_HIGH (PINC & (1 << HREF))
#define HREF_LOW (! (PINC & (1 << HREF)) )

#define VSYNC_HIGH (PINC & (1 << VSYNC))
#define VSYNC_LOW (!(PINC & (1 << VSYNC)) )

#define PCLK_HIGH (PINC & (1 << PCLK))
#define PCLK_LOW (! (PINC & (1 << PCLK)) )


void init_pc_int() {
	// Rising edge of INT2
	//EICRA |= (1 << ISC20) | (1 << ISC21);

	// Enable INT2
	//EIMSK |= 1 << INT2;

	PCICR |= 1 << PCIE2;
	PCMSK2 |= 1 << VSYNC;
}


void init_watchdog() {
	WDTCSR |= (1 << WDIE) | (1 << WDE);
	WDTCSR |= (1 << WDP0) | (1 << WDP1) | (1 << WDP2) | (1 << WDP3);
}

void check_lines() {
	while (VSYNC_LOW);
	while (VSYNC_HIGH);

	uint8_t rows = 0;

	while (VSYNC_LOW) {
		rows++;
		while (HREF_HIGH);
	}

	print_uint8(rows);
	println(" ");

}

void check_cols() {
	while (HREF_HIGH);
	while (HREF_LOW);

	uint16_t cols = 0;

	while (HREF_HIGH) {
		while (PCLK_LOW);
		cols++;
	}

	print_uint16(cols);
	println(" ");

}

#define BYTES 176
volatile uint8_t bytes[176][76];
volatile uint8_t byte, i;

void sample() {

	while (VSYNC_LOW);
	while (VSYNC_HIGH);

	uint8_t row, col;
	row = col = 0;

	while (VSYNC_LOW) {
		col = 0;

		while (HREF_HIGH) {
			while (PCLK_LOW);
			bytes[row][col++] = PINA;

		}
		row++;

	}

	for (row = 0; row < 176; row++) {
		for (col = 0; col < 76; col++) {
			send_byte(bytes[row][col]);
		}
	}

}

int main() {

	init_usart();
	ENABLE_RX_INTERRUPT;
	init_twi();
	//init_watchdog();
	//init_pc_int();
	sei();
	println("Init");

	while(1);

	return 0;
}
