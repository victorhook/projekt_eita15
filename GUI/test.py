from callback import Callback

def test():
    print("Test!")


cb = Callback()
cb.add_callback(test)

cb.call()