import logging

DEFAULT_OUTPUT = 'log'
DEFAULT_NAME   = 'CrazyCarLog'
DEFAULT_MODE   = 'a'

class Log:

    def __init__(self, name=None, output=None, mode=None):
        name = name if name else DEFAULT_NAME
        self._log = logging.getLogger(name)
        self._log.setLevel(logging.INFO)

        output = output if output else DEFAULT_OUTPUT
        mode = mode if mode else DEFAULT_MODE

        handler = logging.FileHandler(output, mode=mode)
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter('[%(asctime)s] %(message)s', '%H:%M:%S'))

        self._log.addHandler(handler)


    def info(self, msg):
        self._log.info(msg)

    def debug(self, msg):
        self._log.debug(msg)

    def warning(self, msg):
        self._log.warning(msg)

    def error(self, msg):
        self._log.error(msg)

    def critical(self, msg):
        self._log.critical(msg)

log = Log(name='cool', output='cool')
log.info("test")