import os
import config
from piece import Piece
from math import ceil

class File():
    def __init__(self, file, piece_length, offset):
        dirname = os.path.dirname(file['path'])
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        self.stream = open('./complete/%s' % file['path'], 'wb')
        num_pieces = file['length'] // piece_length
        if num_pieces > 0:
            self.pieces = [Piece(piece_length, False) for i in range(num_pieces)]
        else:
            self.pieces = []
        self.pieces.append(Piece(file['length'] % piece_length, True))
        self.progress = 0
        self.offset = offset

    def write(self):
        while self.pieces[self.progress].complete and not self.progress == -1:
            print('\t\t     writing (%i/%i)' % (self.progress + 1, len(self.pieces)))
            self.stream.write(b''.join(self.pieces[self.progress].blocks))
            self.progress += 1
            if self.progress >= len(self.pieces):
                print('\t\t     🎉')
                self.stream.close()
                self.progress = -1