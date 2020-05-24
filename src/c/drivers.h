#ifndef DRIVERS_H
#define DRIVERS_H

#include <avr/io.h>
#include <avr/interrupt.h>
#define F_CPU 20000000
#include <util/delay.h>

#include "globals.c"
#include "usart.h"

/** ----- INTERRUPTS ----- **/

// Increments an overflow counter for TIMER 0 (US sensor)
ISR(TIMER0_OVF_vect) {
	timer0_overflow++;
	us_sensor_ready++;
}

/** ----- INIT FUNCTINOS ----- **/

// Sets the corresponding trigger-pin as output
void init_us_sensor();

/* Initializes the PWM ports for the motors.
 * These have a frequency of ~ 39 kHz
 * And have TOP level as 64, eg: 100% thrust => OCRXX = 64 */
void init_motor_pwm();

/* Sets honk port as OUT */
void init_honk();

/* Debug function */
void init_adc();

/* Sets correct start values for anoroc */
void init_anoroc(anoroc_control *anoroc);

/* Initializes the timer0, which is used for timeouts and overflows */
void init_timer0();

/* Sets correct LED ports as OUT */
void init_leds();


/** ----- DRIVER FUNCTINOS ----- **/

/* Measures distance in front of Anoroc, wich fairly OK precision, up to ~ 2m */
void measure_distance(anoroc_control *anoroc);

/* Turns on corresponding LEDS */
void led_on(uint8_t led, led_color color);


/** ----- ANOROC CONTROL ----- **/

/* Honks if we need are suppose to! */
void honk_control(anoroc_control *anoroc);

/* Adjusts the leds according to anorocs variables */
void led_control(anoroc_control *anoroc);

/* Checks if Bluetooth is connected */
uint8_t bluetooth_connected();

/* Sends all variables to host machine */
void talk_to_host(anoroc_control *anoroc);

/* Listens to Bluetooth Module, through USART
 * and updates variables Honk status & Motor thrust  */
void listen_to_host(anoroc_control *anoroc);

/* Sets the correct thrust levels for the motors
 * Note: MSB Bit is REVERSE/NOT REVERSE,
 *           Bit 2-7 is thrust level			*/
void steer(anoroc_control *anoroc);

/* Changes connection state and sets honk & led to disconnected */
void disconnect(anoroc_control *anoroc);

/* Changes connection state and sets honk & led to connected */
void connect(anoroc_control *anoroc);


#endif
