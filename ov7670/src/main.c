#include <avr/io.h>
#include <avr/interrupt.h>

#include "usart.h"
#include "twi.h"

#define F_CPU 20000000
#include <util/delay.h>


#define USART_SEND(data) 	while ( !(UCSR0A & (1 << UDRE0)) ); \
							UDR0 = data;
#define ENABLE_RX_INTERRUPT UCSR0B |= 1 << RXCIE0






ISR(USART0_RX_vect) {

	uint8_t command = UDR0, data, addr;

	switch (command) {
	case 0x00:
		addr = read_byte();
		data = twi_r_reg(addr);
		USART_SEND(data);

		break;
	case 0x01:

		twi_start();
		twi_send(0x42, TW_MT_SLA_ACK);
		twi_send(0x01, TW_MT_DATA_ACK);
		twi_stop();

		_delay_ms(1);

		twi_start();
		twi_send(0x43, TW_MR_SLA_ACK);
		uint8_t data = twi_read_nack();
		twi_stop();
		USART_SEND(data);


		break;
	}

}




int main() {

	init_usart();
	twi_init();
	ENABLE_RX_INTERRUPT;
	sei();

	UBRR0 = 10;

	while(1);

	return 0;
}
