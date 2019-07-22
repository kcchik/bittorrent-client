import math
import time
import threading
import hashlib
import struct
import bencode

import config
import cli
import factory
from peer import Peer


class Manager():
    def __init__(self):
        self.lock = threading.Lock()
        self.progress = 0
        self.leftovers = b''
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
        cli.printf(len(self.peers))
        for peer in self.peers:
            peer.start()

        # Wait for metadata pieces to complete
        while config.COMMAND == 'magnet' and not config.PIECE_SIZE:
            time.sleep(0.1)
            if self.pieces and all(piece['complete'] for piece in self.pieces):
                pieces = [piece['value'] for piece in self.pieces]
                info = bencode.bdecode(b''.join(pieces))
                self.info(info)


    def write(self):
        for file in self.files:
            while not file['complete']:
                # Piece is not ready to be written
                if not self.pieces[self.progress]['complete']:
                    return

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
                    self.leftovers = data[piece_size:] if piece_size > 0 else self.leftovers
                    break

                # First piece and not first file
                if not file['started'] and file['offset'] != file['length']:
                    data = self.leftovers
                    self.leftovers = b''
                    file['started'] = True

                file['stream'].write(data)
                self.progress += 1


    def has(self, peer, index):
        self.lock.acquire()
        self.pieces[index]['peers'].add(peer)
        self.lock.release()


    def push(self, peer, index, offset, block):
        self.lock.acquire()
        piece = self.pieces[index]
        piece['blocks'][offset // config.BLOCK_SIZE]['value'] = block
        blocks = [block['value'] for block in piece['blocks']]

        # Piece is complete
        if all(blocks):
            # Validate piece
            if hashlib.sha1(b''.join(blocks)).digest() == piece['value']:
                piece['complete'] = True
                if index == self.progress:
                    self.write()
            else:
                piece['blocks'] = [factory.block() for _ in piece['blocks']]
                piece['peers'].remove(peer)

            # Reset peer
            # self.piece_index = -1
            piece['requesting'] = None
        self.lock.release()


    def next(self, peer):
        # Since peers take an entire piece for themselves, there is a possibility that some peers will idle when there are blocks available
        self.lock.acquire()

        block_index = 0
        piece_index = 0
        piece = self.pieces[piece_index]
        for piece_index, piece in enumerate(self.pieces):
            if not piece['complete'] and peer in piece['peers']:
                for block_index, block in enumerate(piece['blocks']):
                    if not block['requesting']:
                        block['requesting'] = peer
                        break
                else:
                    continue
                break
        else:
            for piece in self.pieces:
                piece['peers'].remove(peer)
                for block in piece['blocks']:
                    if block['requesting'] == peer:
                        block['requesting'] = None
            self.lock.release()
            return None

        block_size = config.BLOCK_SIZE
        if piece_index + 1 == len(self.pieces) and block_index + 1 == len(piece['blocks']):
            block_size = self.length % config.BLOCK_SIZE

        message = struct.pack('>IBIII', 13, 6, piece_index, block_index * config.BLOCK_SIZE, block_size)
        self.lock.release()
        return message
