class Piece():
    def __init__(self, size):
        self.available = False
        self.blocks = [None] * size
        self.done = False

    def complete(self):
        for block in self.blocks:
            if not block:
                return False
        return True

    def data(self):
        return b''.join(self.blocks)
