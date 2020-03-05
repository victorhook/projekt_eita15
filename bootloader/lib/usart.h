#ifndef USART_H
#define USART_H

uint8_t read_byte();

void send_byte(uint8_t data);

void println(const char *msg);

void print(const char *msg);

void print_uint8(uint8_t nbr);

void init_usart();

#endif
