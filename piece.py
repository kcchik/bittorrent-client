class Piece():
    def __init__(self, size):
        self.blocks = [None] * size
        self.state = {
            'complete': False,
            'requesting': None,
        }

    def left(self):
        left = len(self.blocks)
        for block in self.blocks:
            if block:
                left = left - 1
        return left

    def data(self):
        if self.left() == 0:
            return b''.join(self.blocks)
        return b''
