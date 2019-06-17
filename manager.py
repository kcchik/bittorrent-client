import math

import config
from peer import Peer
from piece import Piece
from file import File

class Manager():
    def __init__(self, tracker):
        self.tracker = tracker
        self.progress = 0
        self.offset = 0
        self.files = []
        for file in tracker.torrent.files:
            self.files.append(File(file))
        self.pieces = [Piece(piece_hash) for piece_hash in tracker.torrent.pieces]
        self.pieces[len(tracker.torrent.pieces) - 1].blocks = [None] * math.ceil(tracker.torrent.length % config.PIECE_LENGTH / config.BLOCK_LENGTH)
        self.peers = [Peer(self, address) for address in tracker.addresses]

    def start(self):
        for peer in self.peers:
            peer.start()

    def write(self):
        initial = b''
        for file in self.files:
            while not file.complete:
                if not self.pieces[self.progress].complete:
                    return
                file.stream.write(initial)
                initial = b''
                print(''.ljust(20), ('… {}/{}'.format(self.progress + 1, len(self.pieces))).ljust(15), file.path)
                data = self.pieces[self.progress].data()
                if self.progress == file.length // config.PIECE_LENGTH + int(self.offset):
                    self.offset += file.length / config.PIECE_LENGTH
                    file.stream.write(data[:file.length % config.PIECE_LENGTH])
                    if file.length % config.PIECE_LENGTH > 0:
                        initial = data[file.length % config.PIECE_LENGTH:]
                    print(''.ljust(20), '🎉'.ljust(14), file.path)
                    file.stream.close()
                    file.complete = True
                    if not any(not file.complete for file in self.files):
                        print(''.ljust(20), 'done!')
                    break
                file.stream.write(data)
                self.progress += 1
