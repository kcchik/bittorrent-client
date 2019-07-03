import threading
import socket
import hashlib
import struct
import sys
import time
import math
import bencode
import bitstring

import config
import cli
import factory

class Peer(threading.Thread):
    def __init__(self, address):
        threading.Thread.__init__(self)
        self.address = address
        self.socket = socket.socket()
        self.socket.settimeout(10)
        self.has = set()
        self.state = {
            'metadata_handshake': False,
            'handshake': False,
            'connected': True,
            'choking': True,
        }
        self.piece_index = -1
        self.metadata_id = -1

    def connect(self):
        try:
            self.socket.connect(self.address)
        except OSError as _:
            self.disconnect()

    def disconnect(self):
        if self.piece_index != -1:
            if config.METHOD == 1:
                config.manager.pieces[self.piece_index]['requesting'] = False
            else:
                config.manager.pieces[config.manager.progress]['blocks'][self.piece_index]['requesting'] -= 1
        self.socket.close()
        self.state['connected'] = False
        sys.exit()

    def run(self):
        self.connect()
        self.send_handshake()
        self.parse_stream()

    def parse_stream(self):
        stream = b''
        while True:
            # cli.printf('Receiving', prefix=self.address[0])
            try:
                packet = self.socket.recv(4096)
            except OSError as _:
                self.disconnect()

            if not packet:
                self.disconnect()

            if not self.state['handshake']:
                packet = self.handle_handshake(packet)

            done = True
            stream += packet
            while len(stream) >= 4:
                length = struct.unpack('>I', stream[:4])[0]
                if length == 0 or len(stream) < length + 4:
                    self.send(bytes(4))
                    done = False
                    break
                message = stream[4:length + 4]
                self.handle(message)
                stream = stream[length + 4:]

            if done:
                if not config.manager.files:
                    if self.metadata_id != -1:
                        self.send_metadata_request()
                elif self.state['choking']:
                    self.send_interested()
                else:
                    if config.METHOD == 1:
                        self.send_request_1()
                    else:
                        self.send_request_2()

    def handle(self, message):
        num = message[0]
        payload = message[1:] if len(message) > 1 else b''

        if num == 0:
            # cli.printf('Choked', prefix=self.address[0])
            self.state['choking'] = True
        elif num == 1:
            # cli.printf('Unchoked', prefix=self.address[0])
            self.state['choking'] = False
        elif num == 4:
            # cli.printf('Have', prefix=self.address[0])
            self.handle_have(payload)
        elif num == 5:
            # cli.printf('Bitfield', prefix=self.address[0])
            self.handle_bitfield(payload)
        elif num == 7:
            # cli.printf('Block', prefix=self.address[0])
            if config.METHOD == 1:
                self.handle_block_1(payload)
            else:
                self.handle_block_2(payload)
        elif num == 20:
            if not config.manager.files:
                if not self.state['metadata_handshake']:
                    cli.printf('Metadata Handshake', prefix=self.address[0])
                    self.handle_metadata_handshake(payload)
                else:
                    # cli.printf('Metadata Piece', prefix=self.address[0])
                    self.handle_metadata_piece(payload)

    def handle_handshake(self, packet):
        pstrlen = packet[0]
        info_hash = struct.unpack('>20s', packet[pstrlen + 9:pstrlen + 29])[0]
        if info_hash != config.tracker.info_hash:
            cli.printf('Info hashes do not match', prefix=self.address[0])
            self.disconnect()
        self.state['handshake'] = True
        return packet[pstrlen + 49:]

    def handle_metadata_handshake(self, payload):
        metadata = dict(bencode.bdecode(payload[1:]).items())
        if 'm' not in metadata or 'metadata_size' not in metadata:
            self.disconnect()
        m = dict(metadata['m'].items())
        if 'ut_metadata' not in m:
            self.disconnect()
        self.metadata_id = m['ut_metadata']
        if not config.manager.pieces:
            num_pieces = math.ceil(metadata['metadata_size'] / config.BLOCK_SIZE)
            config.manager.pieces = [factory.piece() for _ in range(num_pieces)]
        self.state['metadata_handshake'] = True

    def handle_metadata_piece(self, payload):
        i = payload.index(b'ee') + 2
        metadata = dict(bencode.bdecode(payload[1:i]).items())
        if 'msg_type' not in metadata and 'piece' in metadata:
            self.disconnect()
        self.piece_index = metadata['piece']
        piece = config.manager.pieces[self.piece_index]
        if metadata['msg_type'] == 1 and not piece['complete']:
            cli.printf('\033[92m𝑖\033[0m {}/{}'.format(self.piece_index + 1, len(config.manager.pieces)), prefix=self.address[0])
            piece['value'] = payload[i:]
            piece['complete'] = True
        self.piece_index = -1

    def handle_have(self, payload):
        i = struct.unpack('>I', payload)[0]
        self.has.add(i)

    def handle_bitfield(self, payload):
        bit_array = list(bitstring.BitArray(payload))
        self.has.update([i for i, available in enumerate(bit_array) if available])

    def handle_block_1(self, payload):
        i, offset = struct.unpack('>II', payload[:8])
        block = payload[8:]
        if self.piece_index != i:
            return
        piece = config.manager.pieces[i]
        piece['blocks'][offset // config.BLOCK_SIZE]['value'] = block
        if sum(1 for block in piece['blocks'] if not block['value']) == 0:
            if hashlib.sha1(b''.join([block['value'] for block in piece['blocks']])).digest() == piece['value']:
                cli.printf('\033[92m✓\033[0m {}/{}'.format(i + 1, len(config.manager.pieces)), prefix=self.address[0])
                piece['complete'] = True
            else:
                cli.printf('\033[91m✗\033[0m {}/{}'.format(i + 1, len(config.manager.pieces)), prefix=self.address[0])
                piece['blocks'] = [factory.block() for _ in piece['blocks']]
                self.has.remove(i)
            self.piece_index = -1
            piece['requesting'] = False

    def handle_block_2(self, payload):
        i, offset = struct.unpack('>II', payload[:8])
        block = payload[8:]
        if config.manager.progress != i:
            return
        piece = config.manager.pieces[i]
        piece['blocks'][offset // config.BLOCK_SIZE]['value'] = block
        self.piece_index = -1
        if sum(1 for block in piece['blocks'] if not block['value']) == 0:
            if hashlib.sha1(b''.join([block['value'] for block in piece['blocks']])).digest() == piece['value']:
                cli.printf('\033[92m✓\033[0m {}/{}'.format(i + 1, len(config.manager.pieces)), prefix=self.address[0])
                piece['complete'] = True
            else:
                cli.printf('\033[91m✗\033[0m {}/{}'.format(i + 1, len(config.manager.pieces)), prefix=self.address[0])
                piece['blocks'] = [factory.block() for _ in piece['blocks']]
                self.has.remove(i)

    def send(self, message):
        try:
            self.socket.send(message)
        except OSError as _:
            return

    def send_handshake(self):
        pstr = b'BitTorrent protocol'
        pstrlen = bytes([len(pstr)])
        reserved = bytes(8) if config.COMMAND == 'torrent' else b'\x00\x00\x00\x00\x00\x10\x00\x00'
        message = (
            pstrlen
            + pstr
            + reserved
            + config.tracker.info_hash
            + config.tracker.peer_id
        )
        self.send(message)

    def send_metadata_request(self):
        for i, piece in enumerate(config.manager.pieces):
            if not piece['complete']:
                self.piece_index = i
                metadata = bencode.bencode({
                    'msg_type': 0,
                    'piece': self.piece_index,
                })
                message = struct.pack('>IBB', len(metadata) + 2, 20, self.metadata_id) + metadata
                # cli.printf(message, prefix=self.address[0])
                self.send(message)
                break

    def send_interested(self):
        message = struct.pack('>IB', 1, 2)
        self.send(message)

    def send_request_1(self):
        while self.piece_index == -1:
            for i, piece in enumerate(config.manager.pieces):
                if not piece['requesting'] and not piece['complete'] and i in self.has:
                    piece['requesting'] = True
                    self.piece_index = i
                    break
            else:
                time.sleep(0.1)
            if not any(not file['complete'] for file in config.manager.files):
                self.disconnect()
        piece = config.manager.pieces[self.piece_index]
        block_length = config.BLOCK_SIZE
        if (self.piece_index + 1 == len(config.manager.pieces) and sum(1 for block in piece['blocks'] if not block['value']) == 1):
            block_length = config.manager.length % config.BLOCK_SIZE
        offset = (len(piece['blocks']) - sum(1 for block in piece['blocks'] if not block['value'])) * config.BLOCK_SIZE
        message = struct.pack(
            '>IBIII',
            13,
            6,
            self.piece_index,
            offset,
            block_length
        )
        self.send(message)

    def send_request_2(self):
        progress = config.manager.progress
        piece = config.manager.pieces[progress]
        while self.piece_index == -1:
            progress = config.manager.progress
            if progress in self.has:
                piece = config.manager.pieces[progress]
                for i, block in enumerate(piece['blocks']):
                    if block['requesting'] < 1 and not block['value']:
                        block['requesting'] += 1
                        self.piece_index = i
                        cli.printf('\033[92mb\033[0m {}/{}'.format(i + 1, len(piece['blocks'])), prefix=self.address[0])
                        break
            if self.piece_index != -1:
                time.sleep(0.1)
            if not any(not file['complete'] for file in config.manager.files):
                self.disconnect()
        message = struct.pack(
            '>IBIII',
            13,
            6,
            progress,
            self.piece_index * config.BLOCK_SIZE,
            piece['blocks'][self.piece_index]['length']
        )
        self.send(message)
