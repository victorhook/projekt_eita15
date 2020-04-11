import logging
import os


class Logger:

    def __init__(self):

        self.log = logging.getLogger()
        self.log.setLevel(logging.INFO)

        log_file = os.path.join(self.base_dir, self.log_file)

        handler = logging.FileHandler(log_file, mode=self.log_mode)
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter('[%(asctime)s] %(message)s', '%H:%M:%S'))

        self.log.addHandler(handler)
        self.log.info('New session started')
