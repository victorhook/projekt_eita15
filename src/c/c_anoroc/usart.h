#ifndef USART_H
#define USART_H

#ifndef BAUD
#define BAUD 115200
#endif

#ifndef F_CPU
#define F_CPU 20000000
#endif

/* Calculation for setting the right baud rate in the UBRR register */
#define BAUDR (F_CPU/(16*BAUD))

/* Initializes the Usart with the given baud rate */
void init_usart();

/* Sends a single byte through USART
 * A macro is used to save function overhead */
#define send_byte(data) {\
		while (! (UCSR0A & (1 << UDRE0)) ); \
		UDR0 = data;\
	}

/* Reads a single byte through USART */
uint8_t read_byte();

/* Sends an array of bytes, with a given length */
void send_bytes(uint8_t *bytes, uint8_t len);

/* Flushes the Usart stream, removing any data that's stuck */
void flush();

/* Sends a given string (expecting it to be NULL-terminated! */
void print(uint8_t *data);

/* Sends a given string (expecting it to be NULL-terminated! */
void println(uint8_t *data);

/* Sends an uin8t as ascii */
void print_uint8(uint8_t data);

/* Sends an uint16 as ascii */
void print_uint16(uint16_t data);


#endif
