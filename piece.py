import math

import config
from block import Block

class Piece():
    def __init__(self, value=b''):
        self.value = value
        self.blocks = [Block() for _ in range(math.ceil(config.piece_length / config.block_length))]
        self.complete = False
        self.requesting = False

    def left(self):
        return sum(1 for block in self.blocks if not block.value)

    def block_offset(self):
        return (len(self.blocks) - self.left()) * config.block_length

    def data(self):
        return b''.join([block.value for block in self.blocks])
