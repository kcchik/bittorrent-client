import os

class File():
    def __init__(self, file):
        self.length = file['length']
        self.path = file['path']
        dirname = os.path.dirname(file['path'])
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        self.stream = open('./complete/%s' % file['path'], 'wb')
        self.complete = False
