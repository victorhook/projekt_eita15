#ifndef ANOROC_UTILS_H
#define ANOROC_UTILS_H

#include <avr/io.h>
#include <avr/interrupt.h>
#define F_CPU 20000000
#include <util/delay.h>

#include "globals.c"
#include "usart.h"
#include "leds.h"

#define ECHO_PIN PA1
#define TRIG_PIN PA2
#define ULTRA_SENSOR_PORT PORTA
#define ULTRA_SENSOR_PIN PINA
#define ULTRA_SENSOR_DDR DDRA

#define PWM_MOTOR_DDR DDRD
#define PWM_MOTOR_PIN PORTD5

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
 * to actual distance at host (to save processing power)   */
uint16_t measure_distance();


/* Initializes the PWM signal for the H-bdrige drv8833
 * The H-bridge wants 50 kHz, although we're at ~39 kHz,
 * which works fine.
 * ICR1 is set as TOP at 64
 * OCR1[A/B] adjusts the PWM.
 * This means an 8-bit signal can easly be adjusted to the PWM
 * by dividing by 4 (X >> 2)									 */
void init_motor_pwm();


/* Syntactic sugar, to set the new PWM signal
 * (In reality, this means chaning the value of the compare register)	*/
#define adjust_pwm(pwm_value) {\
	OCR1A = pwm_value;\
	OCR1B = pwm_value;\
}\


/* Debug function */
void init_adc();

#endif
