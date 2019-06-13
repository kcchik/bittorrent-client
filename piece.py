import config
from math import ceil

class Piece():
    def __init__(self, length, last):
        self.length = length
        self.blocks = [None] * ceil(length / config.BLOCK_LENGTH)
        self.complete = False
        self.requesting = False
        self.last = last

    def left(self):
        left = len(self.blocks)
        for block in self.blocks:
            if block:
                left -= 1
        return left

    def data(self):
        if self.left() == 0:
            return b''.join(self.blocks)
        return b''
