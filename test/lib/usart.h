#ifndef BAUD
#define BAUD 9600
#endif

#ifndef F_CPU
#define F_CPU 16000000
#endif

#define UBRR F_CPU/16/BAUD-1

uint8_t read_byte();

void send_byte(uint8_t data);

void println(const char *msg);

void print(const char *msg);

void print_uint8(uint8_t nbr);

void init_usart();
