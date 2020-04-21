#ifndef LEDS_H
#define LEDS_H

#define LED_PORT PORTC
#define LED_DDR DDRC
#define LED_RED PORTC2
#define LED_GREEN PORTC1
#define LED_BLUE PORTC0

void init_leds();

void init_bluetooth_status_int();

#endif
