class Callback:

    def __init__(self):
        self._callbacks = []

    def add_callback(self, cb):
        if not cb in self._callbacks:
            self._callbacks.append(cb)
        
    def remove_callback(self, cb):
        self._callbacks.remove(cb)
    
    def call(self, *args):
        for cb in self._callbacks:
            cb(*args)