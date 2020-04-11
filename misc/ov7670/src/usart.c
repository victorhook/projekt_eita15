#include <avr/io.h>
#include "usart.h"

/* Formula doesn't work, use magic numbers straight from Datasheet instead
 * F_CPU = 20 Mhz
 * Baud  = 38400
 */
#define UBRR_BAUD 32

uint8_t read_byte() {
	while (! (UCSR0A  & (1 << RXC0)) );
	return UDR0;
}

void send_byte(uint8_t data) {
	while ( !(UCSR0A & (1 << UDRE0)) );
	UDR0 = data;
}

void println(const char *msg) {
	print(msg);
	send_byte('\r');
	send_byte('\n');
}

void print(const char *msg) {
	while (*msg) {
		send_byte(*msg++);
	}
}

void print_uint8(uint8_t nbr) {
	if (nbr > 100) {
		uint8_t third = nbr / 100 + 48;
		nbr %= 100;
		uint8_t second = nbr / 10 + 48;
		nbr %= 10;
		uint8_t first = nbr + 48;
		send_byte(third);
		send_byte(second);
		send_byte(first);
	} else if (nbr > 10) {
		uint8_t second = nbr / 10 + 48;
		nbr %= 10;
		uint8_t first = nbr + 48;
		send_byte(second);
		send_byte(first);
	} else {
		send_byte(nbr + 48);
	}
}

void print_uint16(uint16_t nbr) {
	if (nbr > 10000) {
		uint8_t fifth = nbr / 10000 + 48;
		nbr %= 10000;
		uint8_t fourth = nbr / 1000 + 48;
		nbr %= 1000;
		uint8_t third = nbr / 100 + 48;
		nbr %= 100;
		uint8_t second = nbr / 10 + 48;
		nbr %= 10;
		uint8_t first = nbr + 48;
		send_byte(fifth);
		send_byte(fourth);
		send_byte(third);
		send_byte(second);
		send_byte(first);
	}
	if (nbr > 1000) {
		uint8_t fourth = nbr / 1000 + 48;
		nbr %= 1000;
		uint8_t third = nbr / 100 + 48;
		nbr %= 100;
		uint8_t second = nbr / 10 + 48;
		nbr %= 10;
		uint8_t first = nbr + 48;
		send_byte(fourth);
		send_byte(third);
		send_byte(second);
		send_byte(first);
	}
	if (nbr > 100) {
		uint8_t third = nbr / 100 + 48;
		nbr %= 100;
		uint8_t second = nbr / 10 + 48;
		nbr %= 10;
		uint8_t first = nbr + 48;
		send_byte(third);
		send_byte(second);
		send_byte(first);
	} else if (nbr > 10) {
		uint8_t second = nbr / 10 + 48;
		nbr %= 10;
		uint8_t first = nbr + 48;
		send_byte(second);
		send_byte(first);
	} else {
		send_byte(nbr + 48);
	}
}

void init_usart() {
	// Set Baud rate
	//UBRR0 = UBRR_BAUD;

	// 1 Mbps baud rate
	//UBRR0 = 1;

	// Enable high speed USART
	//UCSR0A |= 1 << U2X0;

	// Enable RX and TX
	UCSR0B |= (1 << RXEN0) | (1 << TXEN0);

	// Data format: | 1 Start | 8 Data| 1 Stop |
	UCSR0C |= (1 << UCSZ00) | (1 << UCSZ01);
}
