import math

import config

class Piece():
    def __init__(self, piece_hash):
        self.piece_hash = piece_hash
        self.blocks = [None] * math.ceil(config.PIECE_LENGTH / config.BLOCK_LENGTH)
        self.complete = False
        self.requesting = False

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
