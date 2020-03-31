from subprocess import Popen, PIPE

""" Simple API for turning on and off the hotspot to connect with Anoroc """

class Hotspot:
    
    @staticmethod
    def open_hotspot():
        # Clears arp cache

        pipe = Popen(['iw', 'dev'], stdout=PIPE, stdin=PIPE, stderr=PIPE)
        status = str(pipe.stdout.read())

        # Checking if we're already runnig hotspot first!
        if HOTSPOT_NAME not in status:
            # Open hotspot
            Popen(['nmcli', 'connection', 'up', HOTSPOT_NAME], stdout=PIPE, stdin=PIPE, stderr=PIPE)

        # Hotspot should be up and running

    @staticmethod
    def close_hotspot():
        # Close hotspot, catch error msg in stderr, nothing to do with it.
        # nmcli handles any potential issues
        Popen(['nmcli', 'connection', 'down', HOTSPOT_NAME], stdout=PIPE, stdin=PIPE, stderr=PIPE)

    @staticmethod
    def scan_ips():
        # Todo: nmap -sP 10.42.0.0/24
        # This needs sudo
        pass

    @staticmethod
    def get_connected_ip():
        # Check the arp cache for known IP addresses 
        ## ONLY WORKS IF PREVIOUSLY CONNECTED!!!
        pipe = Popen(['arp', '-a'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        stdout = str(pipe.stdout.read())

        # Try to match found IP addressees with the expected one for the hotspot
        connected_ips = re.compile(IP_PATTERN).finditer(stdout)

        # Returns a list of IP addresses connected to hotspot (Should only be one)
        return [ip.group() for ip in connected_ips]
