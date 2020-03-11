#ifndef USART_H
#define USART_H

#define BAUD 115200
#define F_CPU 8000000

uint8_t read_byte();

void send_byte(uint8_t data);

void println(const char *msg);

void print(const char *msg);

void print_uint8(uint8_t nbr);

void print_uint16(uint16_t nbr);

void init_usart();

#endif
