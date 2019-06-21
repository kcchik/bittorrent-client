import os

class File():
    def __init__(self, length, path, offset):
        self.length = length
        self.path = './complete/' + path
        self.offset = offset
        dirname = os.path.dirname(self.path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        self.stream = open(self.path, 'wb')
        self.complete = False
        self.started = False
