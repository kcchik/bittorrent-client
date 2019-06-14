import config
from peer import Peer
from piece import Piece
from file import File

class Manager():
    def __init__(self, tracker):
        self.tracker = tracker
        self.progress = 0
        self.files = []
        offset = 0
        for file in tracker.torrent.files:
            self.files.append(File(file, offset))
            offset += file['length'] // config.PIECE_LENGTH + 1
        self.pieces = [Piece(piece_hash) for piece_hash in tracker.torrent.pieces]
        self.peers = [Peer(self, address) for address in tracker.addresses]

    def start(self):
        for peer in self.peers:
            peer.start()

    def write(self):
        initial = b''
        for file in self.files:
            while True:
                if not self.pieces[self.progress].complete:
                    return
                if file.complete:
                    self.progress == file.offset
                    break
                file.stream.write(initial)
                initial = b''
                print(''.ljust(20), ('… {}/{}'.format(self.progress + 1, len(self.pieces))).ljust(15), file.path)
                data = b''.join(self.pieces[self.progress].blocks)
                if self.progress == file.length // config.PIECE_LENGTH + file.offset:
                    file.stream.write(data[:file.length  % config.PIECE_LENGTH])
                    if file.length % config.PIECE_LENGTH > 0:
                        initial = data[file.length % config.PIECE_LENGTH:]
                    print(''.ljust(20), '🎉'.ljust(14), file.path)
                    file.stream.close()
                    file.complete = True
                    if not any(not file.complete for file in self.files):
                        print(''.ljust(20), 'done!')
                    self.progress += 1
                    break
                file.stream.write(data)
                self.progress += 1
