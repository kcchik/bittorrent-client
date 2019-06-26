import config

class Block():
    def __init__(self):
        self.length = config.block_length
        self.value = b''
        self.requesting = 0
