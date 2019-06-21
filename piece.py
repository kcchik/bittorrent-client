import math

import config

class Piece():
    def __init__(self, value=b''):
        self.value = value
        self.blocks = [None] * math.ceil(config.piece_length / config.block_length)
        self.complete = False
        self.requesting = False

    def left(self):
        return sum(1 for block in self.blocks if not block)

    def block_offset(self):
        return (len(self.blocks) - self.left()) * config.block_length

    def data(self):
        return b''.join(self.blocks)
