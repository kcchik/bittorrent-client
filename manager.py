from math import ceil
from threading import Thread
from peer import Peer
from piece import Piece
import config
import sys

class Manager():
    def __init__(self, tracker):
        self.file = open('./complete/%s' % tracker.torrent.name, 'wb')
        self.progress = 0
        self.tracker = tracker
        size = ceil(tracker.torrent.piece_length / config.BLOCK_SIZE)
        self.pieces = [Piece(size) for piece in tracker.torrent.pieces]
        self.peers = [Peer(id, self, address) for id, address in enumerate(self.tracker.addresses)]

    def start(self):
        for peer in self.peers:
            peer.start()

    def write(self):
        while self.pieces[self.progress].state['complete']:
            print('                     writing (%i/%i)' % (self.progress + 1, len(self.pieces)))
            self.file.write(b''.join(self.pieces[self.progress].blocks))
            self.progress += 1
            if self.progress == len(self.pieces):
                print('                     download complete')
                self.file.close()
                sys.exit(1)
