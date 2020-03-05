#ifndef I2C_H
#define I2C_H


void init_i2c();

uint8_t i2c_exchange_byte(uint8_t data);

void i2c_write(uint8_t *data, uint8_t len);


#endif
