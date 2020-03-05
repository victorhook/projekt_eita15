#include <inttypes.h>
#include <avr/interrupt.h>
#include <avr/pgmspace.h>

#define PAGESIZE 256
/*
void boot_program_page(uint32_t page, uint8_t *buf) {

	uint16_t word;
	uint8_t sreg;

	sreg = SREG;		// Save status reg
	cli();				// Disable interrupts

	eeprom_busy_wait();

	boot_page_erase(page);
	boot_spm_busy_wait();

	// Fill upp whole page ( Page size for atmega1284 = 128 words = 256 Bytes )
	for (uint16_t i = 0; i < SPM_PAGESIZE; i += 2) {
		word = *buf++ | (*buf++ << 8);			// Ram memory is 1 byte program memory is 2 Bytes

		boot_page_fill(page + i, word);
	}

	boot_page_write(page);		// Store buffer in program memory
	boot_spm_busy_wait();		// Wait until memory is written

	boot_rww_enable();

	SREG = sreg;				// Restore status register
	sei();						// Re-enable interrupts
}

/* Initialize the bootloader */

