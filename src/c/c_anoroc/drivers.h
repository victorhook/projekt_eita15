#ifndef ANOROC_UTILS_H
#define ANOROC_UTILS_H

#include <avr/io.h>
#include <avr/interrupt.h>
#include <string.h>

#define F_CPU 20000000
#include <util/delay.h>

#define ECHO_PIN PA1
#define TRIG_PIN PA2
#define ULTRA_SENSOR_PORT PORTA
#define ULTRA_SENSOR_PIN PINA
#define ULTRA_SENSOR_DDR DDRA

// We're using pin PA0 (ADC0) as input
void init_battery_checker();

/* Measures the voltage of the battery and returns
 * it as an uin8t. The Host can then do the conversions
 */
uint8_t measure_battery();

// Sets the correct IO pins for Ultra-sound sensor
void init_distance_measurement();

/* Measures the distance in front of the sensor robot
 * The value returned is raw timer-data and is transformed
 * to actual distance at host (to save processing power)
 */
uint16_t measure_distance();

#endif
