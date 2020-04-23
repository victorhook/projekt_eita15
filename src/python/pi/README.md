These are the files that reside ON the Raspberry Pi.
The video-streaming is done with the PiCamera API.
The python script is controlled with a bash script that is loaded into systemd.

How it works:
1. Systemd starts anoroc.sh service when Raspberry Pi boots
2. anoroc.sh enters an infinite loop and will run until Raspberry Pi is powered off, or the program manually closed
3. anoroc.sh waits until we're connected to a hotspot and ensures that we can ping the host.
4. If not, we keep waiting until we are connected and can communicate.
5. If can we're connected and can communicate, anoroc.sh starts the python script and the PiCamera starts streaming video

