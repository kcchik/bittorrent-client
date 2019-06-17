import math

import config
from peer import Peer
from piece import Piece
from file import File

class Manager():
    def __init__(self, tracker):
        self.tracker = tracker
        self.progress = 0
        self.initial = b''
        self.files = []
        offset = 0
        for file in tracker.torrent.files:
            offset += file['length'] / config.PIECE_LENGTH
            self.files.append(File(file, offset))
        self.pieces = [Piece(piece_hash) for piece_hash in tracker.torrent.pieces]
        self.pieces[len(tracker.torrent.pieces) - 1].blocks = [None] * math.ceil(tracker.torrent.length % config.PIECE_LENGTH / config.BLOCK_LENGTH)
        self.peers = [Peer(self, address) for address in tracker.addresses]

    def start(self):
        for peer in self.peers:
            peer.start()

    def write(self):
        for file in self.files:
            while not file.complete:
                if not self.pieces[self.progress].complete:
                    return
                file.stream.write(self.initial)
                file.a += len(self.initial)
                split = file.length % config.PIECE_LENGTH - len(self.initial)
                print(''.ljust(20), ('… {}/{}'.format(self.progress + 1, len(self.pieces))).ljust(15), file.path)
                data = self.pieces[self.progress].data()
                if self.progress == int(file.offset):
                    file.stream.write(data[:split])
                    file.a += len(data[:split])
                    if split > 0:
                        self.initial = data[split:]
                    print(''.ljust(20), len(data[:split]))
                    print(''.ljust(20), file.a, file.length)
                    print(''.ljust(20), '🎉'.ljust(14), file.path)
                    file.stream.close()
                    file.complete = True
                    if not any(not file.complete for file in self.files):
                        print(''.ljust(20), 'done!')
                    break
                file.stream.write(data)
                file.a += len(data)
                self.progress += 1
                self.initial = b''
