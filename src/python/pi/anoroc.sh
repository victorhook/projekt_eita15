#!/bin/bash

HOST="10.42.0.1"
CAMERA_PROGRAM="/usr/sbin/anoroc.py"

while true; do

	while [[ $(ip route ) != *"${HOST}"* ]] ; do
		echo >> /dev/null
	done

	# Connected to Hotspot!

	# Before we start, let's ensure that we can ping host
	while true ; do
		# -c = Number of pings
		# -W = Timeout
		ping -c 1 -W 1 $HOST >> /dev/null

		# If return code is != 0, we're stuck! (this is good)
		if [ $? ] ; then
			# Ping succeded, continue the program
			break
		fi
	done

	# We're connected and can communicate with host let's start the camera!
	python3 $CAMERA_PROGRAM 

done
