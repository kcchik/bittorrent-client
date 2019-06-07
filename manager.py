from math import ceil
from threading import Thread
from peer import Peer
from piece import Piece
import config

class Manager():
    def __init__(self, tracker):
        self.tracker = tracker
        size = ceil(tracker.torrent.piece_length / config.BLOCK_SIZE)
        self.pieces = [Piece(size) for piece in tracker.torrent.pieces]
        self.peers = [Peer(id, self, address) for id, address in enumerate(self.tracker.addresses)]

    def start(self):
        for peer in self.peers:
            peer.start()

    def complete(self):
        for piece in self.pieces:
            if not piece.state['complete']:
                return False
        else:
            return True

    def write(self):
        file = open('./complete/%s' % self.tracker.torrent.name, 'wb')
        for piece in self.pieces:
            file.write(b''.join(piece.blocks))
        file.close()