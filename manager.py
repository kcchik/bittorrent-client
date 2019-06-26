import math
import time
import bencode
import socket

import config
import cli
from peer import Peer
from piece import Piece
from block import Block
from file import File

class Manager():
    def __init__(self, tracker):
        self.tracker = tracker
        self.spinner = cli.spinner()
        self.has_info = False
        self.progress = 0
        self.length = 0
        self.peers = [Peer(self, address) for address in tracker.addresses]
        self.files = []
        self.pieces = []
        self.metadata_pieces = []

    def info(self, info):
        config.piece_length = info['piece length']
        if 'files' in info:
            for file in info['files']:
                self.length += file['length']
                self.files.append(File(file['length'], file['path'][0], self.length))
        else:
            self.length = info['length']
            self.files = [File(self.length, info['name'], self.length)]
        piece_hashes = [info['pieces'][i:i + 20] for i in range(0, len(info['pieces']), 20)]
        self.pieces = [Piece(piece_hash) for piece_hash in piece_hashes]
        self.pieces[-1].blocks = [Block() for _ in range(math.ceil(self.length % config.piece_length / config.block_length))]
        self.pieces[-1].blocks[-1].length = self.length % config.block_length
        self.has_info = True
        for i, peer in enumerate(self.peers):
            if not peer.state['connected']:
                self.peers[i] = Peer(self, self.tracker.addresses[i])
                self.peers[i].start()


    def start(self):
        if not config.verbose:
            self.spinner.start()
        for peer in self.peers:
            peer.start()

        while config.command == 'magnet' and not self.has_info:
            time.sleep(0.1)
            if self.metadata_pieces:
                for i, piece in enumerate(self.metadata_pieces):
                    if not piece.value:
                        break
                else:
                    info = bencode.bdecode(b''.join([piece.value for piece in self.metadata_pieces]))
                    self.info(info)

        leftovers = b''
        while any(not file.complete for file in self.files) and any(peer for peer in self.peers if peer.state['connected']):
            time.sleep(0.1)
            for file in self.files:
                leftovers = self.write(file, leftovers)

        for peer in self.peers:
            peer.disconnect()
        cli.printf('🎉')

    def write(self, file, leftovers):
        while not file.complete:
            if not self.pieces[self.progress].complete:
                return leftovers

            cli.printf(('… {}/{}'.format(self.progress + 1, len(self.pieces))).ljust(15) + file.path)
            if not config.verbose:
                if not self.spinner.event.is_set():
                    self.spinner.event.set()
                    print('\r\033[92m✔\033[0m Connected!')
                cli.loading(self.progress + 1, len(self.pieces))
            data = self.pieces[self.progress].data()
            if self.progress == int(file.offset / config.piece_length):
                piece_length = file.offset % config.piece_length
                file.stream.write(data[:piece_length])
                if piece_length > 0:
                    leftovers = data[piece_length:]
                cli.printf('Complete'.ljust(14) + file.path)
                file.stream.close()
                file.complete = True
                return leftovers

            if not file.started or file.offset != file.length:
                data = leftovers
                leftovers = b''
                file.started = True
            file.stream.write(data)
            self.progress += 1
        return leftovers
