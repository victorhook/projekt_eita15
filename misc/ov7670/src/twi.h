#ifndef TWI_H_
#define TWI_H_

#ifndef F_CPU
#define F_CPU 20000000
#endif

#include <avr/io.h>
#include <util/twi.h>
#include <util/delay.h>

void twi_start();

void twi_stop();

void twi_send(uint8_t data, uint8_t status);

uint8_t twi_read_nack();

uint8_t twi_read_ack();

uint8_t twi_r_reg(uint8_t addr);

#endif
