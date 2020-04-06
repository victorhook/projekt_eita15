#include <avr/io.h>
#include "usart.h"

/* Initializes the Usart with the given baud rate */
void init_usart() {

	// Baud rate register
	UBRR0 = BAUDR;

	// Enable Recieve and transmit
	UCSR0B |= (1 << RXEN0) | (1 << TXEN0);

	// Data format: | 1 START | 8 DATA | 1 STOP |
	UCSR0C |= (1 << UCSZ00) | (1 << UCSZ01);

	// Flush pipe from old data and we're done!
	flush();

}

/* Sends a single byte through USART */
void send_byte(uint8_t data) {
	// Wait until transmit buffer is empty
	while (! (UCSR0A & (1 << UDRE0)) );
	// Put data in data register
	UDR0 = data;
}

/* Reads a single byte through USART */
uint8_t read_byte() {
	// Wait until data is received
	while ( !(UCSR0A & (1 << RXC0)) );
	// Return new data
	return UDR0;
}

/* Flushes the Usart stream, removing any data that's stuck */
void flush() {
	uint8_t tmp;
	while ( (UCSR0A & (1 << RXC0)) ) {
		tmp = UDR0;
	}
}

/* Sends a given string (expecting it to be NULL-terminated! */
void print(uint8_t *data) {
	while (*data) {
		send_byte(*data++);
	}
}

/* Sends a given string (expecting it to be NULL-terminated! */
void println(uint8_t *data) {
	while (*data) {
		send_byte(*data++);
	}
	send_byte('\r');
	send_byte('\n');
}

/* Sends an uin8t as ascii */
void print_uint8(uint8_t data) {

	if (data < 10) {
		send_byte(data + 48);
		return;
	}
	if (data < 100) {
		uint8_t second = data / 10;
		send_byte(second + 48);
		send_byte((data % 10) + 48);
		return;
	}
	uint8_t first = data % 10;
	data /= 10;
	uint8_t second = data % 10;
	data /= 10;
	send_byte(data + 48);
	send_byte(second + 48);
	send_byte(first + 48);
}

/* Sends an uint16 as ascii */
void print_uint16(uint16_t data) {

	if (data <= UINT8_MAX) {
		print_uint8(data);
		return;
	}

	if (data < 1000) {
		uint8_t first = data % 10;
		data /= 10;
		uint8_t second = data % 10;
		data /= 10;
		send_byte(data + 48);
		send_byte(second + 48);
		send_byte(first + 48);
		return;
	}

	if (data < 10000) {
		uint8_t first = data % 10;
		data /= 10;
		uint8_t second = data % 10;
		data /= 10;
		uint8_t third = data % 10;
		data /= 10;
		send_byte(data + 48);
		send_byte(third + 48);
		send_byte(second + 48);
		send_byte(first + 48);
		return;
	}

	uint8_t first = data % 10;
	data /= 10;
	uint8_t second = data % 10;
	data /= 10;
	uint8_t third = data % 10;
	data /= 10;
	uint8_t fourth = data % 10;
	data /= 10;
	send_byte(data + 48);
	send_byte(fourth + 48);
	send_byte(third + 48);
	send_byte(second + 48);
	send_byte(first + 48);
}
