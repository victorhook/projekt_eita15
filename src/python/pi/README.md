These are the files that reside ON the Raspberry Pi.
The main video-streaming is done from the python script, here's all the logic and it's using the PiCamera API.
The python script is controlled and started with a bash script which is loaded into systemd with the anoroc.service unit file.

How it works:
1. Systemd starts anoroc.sh service when Raspberry Pi boots
2. anoroc.sh enters an infinite loop and will run until Raspberry Pi is powered off, or the program manually closed
3. anoroc.sh waits until we're connected to a hotspot and ensures that we can ping the host.
4. If not, we keep waiting until we are.
5. If can wen ping, anoroc.sh starts the python script and the PiCamera starts streaming
