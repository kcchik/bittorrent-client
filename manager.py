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

        if 'files' in info:
            for file in info['files']:
                self.length += file['length']
                self.files.append(factory.file(file['length'], file['path'][0], self.length))
        else:
            self.length = info['length']
            self.files = [factory.file(self.length, info['name'], self.length)]

        piece_hashes = [info['pieces'][i:i + 20] for i in range(0, len(info['pieces']), 20)]
        num_blocks = math.ceil(self.length % config.PIECE_SIZE / config.BLOCK_SIZE)
        self.pieces = [factory.piece(piece_hash) for piece_hash in piece_hashes]
        self.pieces[-1]['blocks'] = [factory.block() for _ in range(num_blocks)]
        self.pieces[-1]['blocks'][-1]['length'] = self.length % config.BLOCK_SIZE

    def start(self):
        config.spinner.start()

        for peer in self.peers:
            peer.start()

        while config.COMMAND == 'magnet' and not self.files:
            time.sleep(0.1)
            if self.pieces and not any(not piece['complete'] for piece in self.pieces):
                pieces = [piece['value'] for piece in self.pieces]
                info = bencode.bdecode(b''.join(pieces))
                self.info(info)

        leftovers = b''
        while (any(not file['complete'] for file in self.files) and any(peer.state['connected'] for peer in self.peers)):
            time.sleep(0.1)
            for file in self.files:
                leftovers = self.write(file, leftovers)

        for peer in self.peers:
            peer.disconnect()
        cli.printf('🎉')

    def write(self, file, leftovers):
        while not file['complete']:
            if not self.pieces[self.progress]['complete']:
                return leftovers

            cli.printf(('… {}/{}'.format(self.progress + 1, len(self.pieces))).ljust(15) + file['path'])
            if not config.VERBOSE and not config.spinner.event.is_set():
                config.spinner.event.set()
                print('\r\033[92m✔\033[0m Connected!')
            cli.loading(self.progress + 1, len(self.pieces), '({} connections)'.format(sum(1 for peer in self.peers if peer.state['connected'])))

            blocks = self.pieces[self.progress]['blocks']
            data = b''.join([block['value'] for block in blocks])

            if self.progress == file['offset'] // config.PIECE_SIZE:
                piece_length = file['offset'] % config.PIECE_SIZE
                file['stream'].write(data[:piece_length])
                if piece_length > 0:
                    leftovers = data[piece_length:]
                cli.printf('Complete'.ljust(14) + file['path'])
                file['stream'].close()
                file['complete'] = True
                return leftovers

            if not file['started'] or file['offset'] != file['length']:
                data = leftovers
                leftovers = b''
                file['started'] = True

            file['stream'].write(data)
            self.progress += 1

        return leftovers
