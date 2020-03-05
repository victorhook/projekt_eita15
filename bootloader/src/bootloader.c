#include <inttypes.h>
#include <avr/interrupt.h>
#include <avr/pgmspace.h>
#include <avr/eeprom.h>
#include <avr/boot.h>

void boot_program_page(uint32_t page, uint8_t *buf) {

	// Disable interrupts and save status register
	cli();
	uint8_t sreg;

	eeprom_busy_wait();		// Should not be needed

	boot_page_erase(page);	// Erase flash page
	boot_spm_busy_wait();	// Wait until SPM instructions are done


	// Fills a temporary buffer for the page to be programmed
	for (uint16_t i = 0; i < SPM_PAGESIZE; i += 2) {

		uint16_t word = *buf++ | (*buf++ << 8);		// Form a word from two bytes, little-endian style

		boot_page_fill(page + i, word);				// Fill temporary flash page buffer
	}

	boot_page_write(page);  // Writes data from buffer to flash
	boot_spm_busy_wait();	// Wait until data is written
	boot_rww_enable();		// Re-enable the RWW-section

	// Re-enable interrupts and restore status register
	SREG = sreg;
	sei();
}
