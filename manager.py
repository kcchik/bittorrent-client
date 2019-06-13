from math import ceil
from threading import Thread
from peer import Peer
from piece import Piece
from file import File
import config
import sys
import os

class Manager():
    def __init__(self, tracker):
        self.tracker = tracker
        self.files = []
        offset = 0
        for file in tracker.torrent.files:
            self.files.append(File(file, tracker.torrent.piece_length, offset))
            offset += file['length'] // tracker.torrent.piece_length
        self.peers = [Peer(self, address) for address in tracker.addresses]

    def start(self):
        for peer in self.peers:
            peer.start()

    def write(self):
        for file in self.files:
            file.write()