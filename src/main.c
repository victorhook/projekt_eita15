#include <avr/io.h>
//#include "usart.h"

#define F_CPU 1843200UL

#include <util/delay.h>

#ifndef BAUD
#define BAUD 9600
#endif

#ifndef F_CPU
#define F_CPU 1000000
#endif

#define UBRR F_CPU/16/BAUD-1

void transmitByte(uint8_t data) {
                                     /* Wait for empty transmit buffer */
  loop_until_bit_is_set(UCSR0A, UDRE0);
  UDR0 = data;                                            /* send data */
}


int main() {

	UBRR0H = (103 >> 8);
  	UBRR0L = 103;

	UCSR0B = (1 << TXEN0) | (1 << RXEN0);
    UCSR0C = (1 << UCSZ01) | (1 << UCSZ00);   

	while (1) {
		transmitByte('a');
	}


	return 0;
}