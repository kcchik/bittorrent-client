import math

import config

class Piece():
    def __init__(self, hash):
        self.hash = hash
        self.blocks = [None] * math.ceil(config.PIECE_LENGTH / config.BLOCK_LENGTH)
        self.complete = False
        self.requesting = False

    def left(self):
        left = len(self.blocks)
        for block in self.blocks:
            if block:
                left -= 1
        return left

    def block_offset(self):
        return (len(self.blocks) - self.left()) * config.BLOCK_LENGTH

    def data(self):
        return b''.join(self.blocks)
