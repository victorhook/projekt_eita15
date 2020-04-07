.global DELAY

DELAY:
	ldi  r18, 66
	REPEAT:
		dec r18
		brne REPEAT
	ret
