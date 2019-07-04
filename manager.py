import math
import time
import bencode

import config
import cli
import factory
from peer import Peer


class Manager():
    def __init__(self):
        self.progress = 0
        self.length = 0
        self.peers = [Peer(address) for address in config.tracker.addresses]
        self.files = []
        self.pieces = []


    def info(self, info):
        config.PIECE_SIZE = info['piece length']

        # Multiple files
        if 'files' in info:
            for file in info['files']:
                self.length += file['length']
                self.files.append(factory.file(file['length'], file['path'][0], self.length))
        # Single file
        else:
            self.length = info['length']
            self.files = [factory.file(self.length, info['name'], self.length)]

        # Initialize pieces
        piece_hashes = [info['pieces'][i:i + 20] for i in range(0, len(info['pieces']), 20)]
        num_blocks = math.ceil(self.length % config.PIECE_SIZE / config.BLOCK_SIZE)
        self.pieces = [factory.piece(piece_hash) for piece_hash in piece_hashes]
        self.pieces[-1]['blocks'] = [factory.block() for _ in range(num_blocks)]
        self.pieces[-1]['blocks'][-1]['length'] = self.length % config.BLOCK_SIZE

        # Reconnect peers
        for peer in self.peers:
            if config.COMMAND == 'magnet' and not peer.state['connected']:
                peer = Peer(peer.address)
                peer.start()

        cli.connected()
        cli.loading(0, len(self.pieces), '({} connections)'.format(sum(1 for peer in self.peers if peer.state['connected'])))


    def start(self):
        cli.connecting()
        for peer in self.peers:
            peer.start()

        # Wait for metadata pieces to complete
        while config.COMMAND == 'magnet' and not self.files:
            time.sleep(0.1)
            if self.pieces and all(piece['complete'] for piece in self.pieces):
                pieces = [piece['value'] for piece in self.pieces]
                info = bencode.bdecode(b''.join(pieces))
                self.info(info)

        leftovers = b''
        # Wait for pieces to be written
        while any(not file['complete'] for file in self.files) and any(peer.state['connected'] for peer in self.peers):
            time.sleep(0.1)
            for file in self.files:
                leftovers = self.write(file, leftovers)

        for peer in self.peers:
            peer.disconnect()


    def write(self, file, leftovers):
        while not file['complete']:
            # Piece is not ready to be written
            if not self.pieces[self.progress]['complete']:
                return leftovers

            cli.printf(('… {}/{}'.format(self.progress + 1, len(self.pieces))).ljust(15) + file['path'])
            cli.loading(self.progress + 1, len(self.pieces), '({} connections)'.format(sum(1 for peer in self.peers if peer.state['connected'])))

            blocks = self.pieces[self.progress]['blocks']
            data = b''.join([block['value'] for block in blocks])

            # Last piece
            if self.progress == file['offset'] // config.PIECE_SIZE:
                piece_size = file['offset'] % config.PIECE_SIZE
                file['stream'].write(data[:piece_size])
                file['stream'].close()
                file['complete'] = True
                cli.printf('Complete'.ljust(14) + file['path'])
                leftovers = data[piece_size:] if piece_size > 0 else leftovers
                break

            # First piece and not first file
            if not file['started'] and file['offset'] != file['length']:
                data = leftovers
                leftovers = b''
                file['started'] = True

            file['stream'].write(data)
            self.progress += 1

        return leftovers
