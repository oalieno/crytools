#!/usr/bin/env python3
import signal

class Timeout:
    '''
    http://stackoverflow.com/a/22348885
    '''
    def __init__(self, seconds = 5):
        self.seconds = seconds

    def handle_timeout(self, signum, frame):
        raise TimeoutError()

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, type, value, traceback):
        signal.alarm(0)

def timeout(t = 5):
    def decorator_wrapper(func):
        def wrapper(*args, **kwargs):
            try:
                with Timeout(t):
                    func(*args, **kwargs)
            except TimeoutError:
                handle()
        return wrapper
    return decorator_wrapper

def l2b(x, byteorder = 'big'):
    L = 1
    while x >= (1 << (L * 8)):
        L *= 2
    l = L // 2
    h = L
    while l != h:
        m = (l + h) // 2
        if x >= (1 << (m * 8)):
            l = m + 1
        else:
            h = m
    return int(x).to_bytes(h, byteorder)

def b2l(x, byteorder = 'big'):
    return int.from_bytes(x, byteorder)

def xor(x, y):
    return bytes([a ^ b for a, b in zip(x, y)])
