from math import ceil
from threading import Thread
from peer import Peer
from piece import Piece
import config

class Manager():
    def __init__(self, tracker):
        self.tracker = tracker
        self.peers = [Peer(self, address) for address in self.tracker.addresses]
        size = ceil(tracker.torrent.piece_length / config.BLOCK_SIZE)
        self.pieces = [Piece(size)] * len(tracker.torrent.pieces)

    def start(self):
        for peer in self.peers:
            peer.start()
