# Device information
MCU    = atmega1284
F_CPU  = 16000000

# Programmer args
BAUD       = 19200
DEVICE     = m1284p
PORT       = /dev/ttyACM0
PROGRAMMER = avrisp

# Compilation variables
CC      = avr-gcc -mmcu=$(MCU)
OBJCOPY = avr-objcopy
OBJDUMP = avr-objdump

# FILENAME is the file with the main() program. 
# All files are built into the build/ directory
FILENAME = main
TARGET   = build/$(FILENAME)
SOURCES  = src/$(FILENAME).c
OBJECTS  = build/$(FILENAME).o

# For .h files
LIB      = lib

# Compilation flags | -c = Compile only | -g = Debugg info | -O Optimization | -I .h files location
CFLAGS     = -c -g -O0 -I $(LIB)


$(TARGET).hex: $(TARGET).elf
	@$(OBJCOPY) -j .data -j .text -O ihex $< $@
	@echo "> Compilation done. HEX file is in: $(TARGET).hex"

$(TARGET).elf: $(OBJECTS)
	@echo "> Linking $(OBJECTS)..."
	@$(CC) $^ -o $@

$(OBJECTS): $(SOURCES)
	@echo "> Compiling $(SOURCES)..."
	@$(CC) $(CFLAGS) $^ -o $@


.PHONY: flash, clean
flash: $(TARGET).hex
	avrdude -p $(DEVICE) -b $(BAUD) -P $(PORT) -c $(PROGRAMMER) -U flash:w:$(TARGET).hex

clean:
	@rm -f $(OBJECTS) $(TARGET).elf $(TARGET).hex

show: $(TARGET).elf
	$(OBJDUMP) -d $(TARGET).elf