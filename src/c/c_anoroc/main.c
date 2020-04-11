#include "drivers.h"
#include "usart.h"


#define ACC_X PA3
#define ACC_Y PA4
#define ACC_Z PA5


int main() {

	init_usart();
	//init_battery_checker();
	//init_distance_measurement();

	println("init...");


	//ADMUX |= (1 << REFS0);
	//ADMUX |= (1 << ADLAR);

	#define ADC_ACC_X 99
	#define ADC_ACC_Y 100
	#define ADC_ACC_Z 101

	ADMUX = ADC_ACC_X;

	ADMUX |= (1 << MUX1) | (1 << MUX0);
	ADCSRA |= (1 << ADPS0) | (1 << ADPS1) | (1 << ADPS2);

	// Enable ADC
	ADCSRA |= (1 << ADEN);

	uint8_t results[3];

	while (1) {

		ADMUX = ADC_ACC_X;
		ADCSRA |= (1 << ADSC);
		while (ADCSRA & (1 << ADSC));
		results[0] = ADCH;

		ADMUX = ADC_ACC_Y;
		ADCSRA |= (1 << ADSC);
		while (ADCSRA & (1 << ADSC));
		results[1] = ADCH;

		ADMUX = ADC_ACC_Z;
		ADCSRA |= (1 << ADSC);
		while (ADCSRA & (1 << ADSC));
		results[2] = ADCH;

		send_bytes(results, sizeof(results));
		_delay_ms(10);

	}

	return 0;
}
