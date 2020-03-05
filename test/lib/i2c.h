#ifndef I2C_H
#define I2C_H

#define I2C_DDR DDRC
#define SCL_PIN PORTC1
#define SDA_PIN PORTC1

void init_i2c();

void i2c_wait_for_complete();

void i2c_start();

void i2c_stop();

uint8_t i2c_read_ack();

uint8_t i2c_read_no_ack();

void i2c_send(uint8_t data);


#endif
