import hashlib
import math
import struct
import threading

import cli
import config
import factory
from peer import Peer


class Manager():
    def __init__(self, info):
        config.PIECE_SIZE = info['piece length']
        self.lock = threading.Lock()
        self.progress = 0
        self.leftovers = b''

        self.peers = [Peer(address) for address in config.tracker.addresses]

        self.length = 0
        self.files = []
        # Multiple files
        if 'files' in info:
            for file in info['files']:
                self.length += file['length']
                self.files.append(factory.file(file['length'], file['path'][0], self.length))
        # Single file
        else:
            self.length = info['length']
            self.files = [factory.file(self.length, info['name'], self.length)]

        piece_hashes = [info['pieces'][i:i + 20] for i in range(0, len(info['pieces']), 20)]
        num_blocks = math.ceil(self.length % config.PIECE_SIZE / config.BLOCK_SIZE)

        # Initialize pieces
        self.pieces = [factory.piece(piece_hash) for piece_hash in piece_hashes]
        self.pieces[-1]['blocks'] = [factory.block() for _ in range(num_blocks)]
        self.pieces[-1]['blocks'][-1]['length'] = self.length % config.BLOCK_SIZE


    def start(self):
        for peer in self.peers:
            peer.start()


    def disconnect(self, address):
        self.lock.acquire()
        for piece in self.pieces:
            piece['peers'].discard(address)
            for block in piece['blocks']:
                if block['requesting'] == address:
                    block['requesting'] = None
        for peer in self.peers:
            if peer.address == address:
                self.peers.remove(peer)
        self.lock.release()


    def has(self, address, index):
        self.lock.acquire()
        self.pieces[index]['peers'].add(address)
        self.lock.release()


    def next(self, address):
        self.lock.acquire()

        block_index = 0
        piece_index = 0
        piece = self.pieces[piece_index]
        for piece_index, piece in enumerate(self.pieces):
            if not piece['complete'] and address in piece['peers']:
                for block_index, block in enumerate(piece['blocks']):
                    if not block['requesting']:
                        block['requesting'] = address
                        break
                else:
                    continue
                break
        else:
            self.lock.release()
            return None

        block_size = config.BLOCK_SIZE
        if piece_index + 1 == len(self.pieces) and block_index + 1 == len(piece['blocks']):
            block_size = self.length % config.BLOCK_SIZE

        message = struct.pack('>IBIII', 13, 6, piece_index, block_index * config.BLOCK_SIZE, block_size)
        self.lock.release()
        return message


    def push(self, address, index, offset, block):
        self.lock.acquire()
        piece = self.pieces[index]
        piece['blocks'][offset // config.BLOCK_SIZE]['value'] = block
        blocks = [block['value'] for block in piece['blocks']]

        success = True

        # Piece is complete
        if all(blocks):
            # Validate piece
            if hashlib.sha1(b''.join(blocks)).digest() == piece['value']:
                piece['complete'] = True
                if index == self.progress:
                    self.write()
            else:
                piece['blocks'] = [factory.block() for _ in piece['blocks']]
                piece['peers'].remove(address)
                success = False

        self.lock.release()
        return success


    def write(self):
        for file in self.files:
            while not file['complete']:
                # Piece is not ready to be written
                if not self.pieces[self.progress]['complete']:
                    return

                cli.printf(('… {}/{}'.format(self.progress + 1, len(self.pieces))).ljust(15) + file['path'])
                cli.loading(self.progress + 1, len(self.pieces))

                blocks = self.pieces[self.progress]['blocks']
                data = b''.join([block['value'] for block in blocks])

                # Last piece of the file
                if self.progress == file['offset'] // config.PIECE_SIZE:
                    piece_size = file['offset'] % config.PIECE_SIZE
                    file['stream'].write(data[:piece_size])
                    file['stream'].close()
                    self.leftovers = data[piece_size:] if piece_size > 0 else self.leftovers
                    file['complete'] = True
                    cli.printf('Complete'.ljust(14) + file['path'])
                    break

                # Write leftover bytes from the last piece of the previous file
                if not file['started'] and file['offset'] != file['length']:
                    data = self.leftovers
                    self.leftovers = b''
                    file['started'] = True

                file['stream'].write(data)
                self.progress += 1
