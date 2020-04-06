#ifndef ANOROC_UTILS_H
#define ANOROC_UTILS_H

// We're using pin PA0 (ADC0) as input
void init_battery_checker();

/* Measures the voltage of the battery and returns
 * it as an uin8t. The Host can then do the conversions
 */
uint8_t battery_measure();

#endif
