import threading
import socket
import hashlib
import struct
import bitstring
import sys
import time
import bencode
import math

import config
from piece import Piece

class Peer(threading.Thread):
    def __init__(self, manager, address):
        threading.Thread.__init__(self)
        self.manager = manager
        self.address = address
        self.socket = socket.socket()
        self.socket.settimeout(10)
        self.state = {
            'metadata_handshake': False,
            'handshake': False,
            'connected': True,
            'choking': True,
        }
        self.has = set()
        self.piece_index = -1
        self.metadata_id = -1
        self.metadata_piece_index = -1

    def connect(self):
        try:
            self.socket.connect(self.address)
        except OSError as e:
            self.disconnect()

    def disconnect(self):
        if self.piece_index != -1:
            self.manager.pieces[self.piece_index].requesting = False
        self.socket.close()
        self.state['connected'] = False
        sys.exit()

    def run(self):
        self.connect()
        self.send_handshake()
        messages = b''
        while True:
            try:
                packet = self.socket.recv(4096)
            except OSError as e:
                self.disconnect()

            if not len(packet):
                self.disconnect()

            if not self.state['handshake']:
                packet = self.handle_handshake(packet)

            messages += packet
            while len(messages) >= 4:
                length = struct.unpack('>I', messages[:4])[0]
                if length == 0 or len(messages) < length + 4:
                    break
                message = messages[4:length + 4]
                self.handle(message)
                self.respond()
                messages = messages[length + 4:]

    def handle(self, message):
        type = message[0]
        payload = b''
        if len(message) > 1:
            payload = message[1:]

        # self.printo('Type {}'.format(type))

        if type == 0:
            self.state['choking'] = True
        elif type == 1:
            self.state['choking'] = False
        elif type == 4:
            self.handle_have(payload)
        elif type == 5:
            self.handle_bitfield(payload)
        elif type == 7:
            self.handle_block(payload)
        elif type == 20:
            if not self.state['metadata_handshake']:
                self.handle_metadata_handshake(payload)
            else:
                self.handle_metadata_piece(payload)

    def handle_handshake(self, packet):
        pstrlen = packet[0]
        info_hash = struct.unpack('>20s', packet[pstrlen + 9:pstrlen + 29])[0]
        if info_hash != self.manager.tracker.info_hash:
            self.printo('Info hashes do not match')
            self.disconnect()
        self.state['handshake'] = True
        # self.printo('Handshake')
        return packet[pstrlen + 49:]

    def handle_metadata_handshake(self, payload):
        metadata = dict(bencode.bdecode(payload[1:]).items())
        if 'm' in metadata:
            m = dict(metadata['m'].items())
            self.metadata_id = m['ut_metadata'] if 'ut_metadata' in m else -1
        if 'metadata_size' in metadata:
            if not self.manager.metadata_pieces:
                self.manager.metadata_pieces = [Piece() for i in range(math.ceil(metadata['metadata_size'] / config.block_length))]
        self.state['metadata_handshake'] = True

    def handle_metadata_piece(self, payload):
        i = payload.index(b'ee') + 2
        metadata = dict(bencode.bdecode(payload[1:i]).items())
        if not 'msg_type' in metadata and 'piece' in metadata:
            return
        metadata_type = metadata['msg_type']
        self.metadata_piece_index = metadata['piece']
        piece = self.manager.metadata_pieces[self.metadata_piece_index]
        if metadata_type == 1 and not piece.complete:
            self.printo('\033[92m𝑖\033[0m {}/{}'.format(self.metadata_piece_index + 1, len(self.manager.metadata_pieces)))
            piece.value = payload[i:]
            piece.complete = True
        else:
            self.printo('\033[91m𝑖\033[0m {}/{}'.format(self.metadata_piece_index + 1, len(self.manager.metadata_pieces)))
        self.metadata_piece_index = -1

    def handle_have(self, payload):
        i = struct.unpack('>I', payload)[0]
        self.has.add(i)

    def handle_bitfield(self, payload):
        bit_array = list(bitstring.BitArray(payload))
        self.has.update([i for i, available in enumerate(bit_array) if available])

    def handle_block(self, payload):
        i, offset = struct.unpack('>II', payload[:8])
        block = payload[8:]
        if self.piece_index != i:
            return
        piece = self.manager.pieces[i]
        piece.blocks[offset // config.block_length] = block
        if piece.left() == 0:
            if hashlib.sha1(piece.data()).digest() == piece.value:
                self.printo('\033[92m✓\033[0m {}/{}'.format(i + 1, len(self.manager.pieces)))
                piece.complete = True
            else:
                self.printo('\033[91m✗\033[0m {}/{}'.format(i + 1, len(self.manager.pieces)))
                piece.blocks = [None] * len(piece.blocks)
                self.has.remove(i)
            self.piece_index = -1
            piece.requesting = False

    def respond(self):
        if not self.manager.has_info and self.metadata_id != -1:
            self.send_metadata_request()
        elif self.state['choking']:
            self.send_interested()
        else:
            self.send_request()

    def send(self, message):
        try:
            self.socket.send(message)
        except OSError as e:
            return

    def send_handshake(self):
        pstr = b'BitTorrent protocol'
        pstrlen = bytes([len(pstr)])
        reserved = b'\x00\x00\x00\x00\x00\x10\x00\x00' if config.is_magnet else bytes(8)
        message = pstrlen + pstr + reserved + self.manager.tracker.info_hash + self.manager.tracker.peer_id
        self.send(message)

    def send_metadata_request(self):
        for i, piece in enumerate(self.manager.metadata_pieces):
            if not piece.complete:
                self.metadata_piece_index = i
                dict = bencode.bencode({
                    'msg_type': 0,
                    'piece': self.metadata_piece_index,
                })
                message = struct.pack('>IBB', len(dict) + 2, 20, self.metadata_id) + dict
                self.send(message)
                break

    def send_interested(self):
        message = struct.pack('>IB', 1, 2)
        self.send(message)

    def send_request(self):
        while self.piece_index == -1:
            for i, piece in enumerate(self.manager.pieces):
                if not piece.requesting and not piece.complete and i in self.has:
                    piece.requesting = True
                    self.piece_index = i
                    break
            if not any(not file.complete for file in self.manager.files):
                self.disconnect()
            time.sleep(0.1)
        piece = self.manager.pieces[self.piece_index]
        block_length = config.block_length
        if self.piece_index + 1 == len(self.manager.pieces) and piece.left() == 1:
            block_length = self.manager.length % config.block_length
        message = struct.pack('>IBIII', 13, 6, self.piece_index, piece.block_offset(), block_length)
        self.send(message)

    def printo(self, message):
        print(self.address[0].ljust(20), message)
