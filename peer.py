import threading
import socket
import struct
import sys
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
        except OSError as e:
            # self.printf('Failed to connect: {}'.format(e))
            self.disconnect()


    def disconnect(self):
        if self.piece_index != -1:
            config.manager.pieces[self.piece_index]['requesting'] = False
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
            try:
                packet = self.socket.recv(4096)
            except OSError as e:
                self.printf('Failed to receive: {}'.format(e))
                self.disconnect()

            if not packet:
                self.printf('Empty packet')
                self.disconnect()

            if not self.state['handshake']:
                self.printf('Handshake')
                packet = self.handle_handshake(packet)

            stream_complete = True
            stream += packet
            while len(stream) >= 4:
                length = struct.unpack('>I', stream[:4])[0]
                # Receive blank or message is still incomplete
                if length == 0 or len(stream) < length + 4:
                    self.send(bytes(4))
                    stream_complete = False
                    break
                message = stream[4:length + 4]
                self.handle(message)
                stream = stream[length + 4:]

            if stream_complete:
                if not config.PIECE_SIZE:
                    if self.metadata_id != -1:
                        self.printf('Metadata request')
                        self.send_metadata_request()
                elif self.state['choking']:
                    # self.printf('Interested')
                    self.send_interested()
                else:
                    # self.printf('Request')
                    self.send_request()


    def handle(self, message):
        message_id = message[0]
        payload = message[1:] if len(message) > 1 else b''

        # Choke
        if message_id == 0:
            # self.printf('Choke')
            self.state['choking'] = True
        # Unchoke
        elif message_id == 1:
            # self.printf('Unchoke')
            self.state['choking'] = False
        # Have
        elif message_id == 4:
            # self.printf('Have')
            self.handle_have(payload)
        # Bitfield
        elif message_id == 5:
            # self.printf('Bitfield')
            self.handle_bitfield(payload)
        # Block
        elif message_id == 7:
            # self.printf('Block')
            self.handle_block(payload)
        # Metadata
        elif message_id == 20 and not config.PIECE_SIZE:
            # Handshake
            if not self.state['metadata_handshake']:
                self.printf('Metadata handshake')
                self.handle_metadata_handshake(payload)
            # Piece
            else:
                self.printf('Metadata piece')
                self.handle_metadata_piece(payload)


    def handle_handshake(self, packet):
        pstrlen = packet[0]
        if len(packet) < pstrlen + 29:
            self.printf('Short handshake')
            self.disconnect()
        info_hash = struct.unpack('>20s', packet[pstrlen + 9:pstrlen + 29])[0]

        # Validate handshake
        if info_hash != config.tracker.info_hash:
            self.printf('Bad handshake')
            self.disconnect()

        self.state['handshake'] = True
        return packet[pstrlen + 49:]


    def handle_metadata_handshake(self, payload):
        metadata = dict(bencode.bdecode(payload[1:]).items())

        # Validate metadata
        if any(key not in metadata for key in ['m', 'metadata_size']):
            self.disconnect()
        m = dict(metadata['m'].items())
        if 'ut_metadata' not in m:
            self.disconnect()

        # Initialize metadata piece array
        if not config.manager.pieces:
            num_pieces = math.ceil(metadata['metadata_size'] / config.BLOCK_SIZE)
            config.manager.pieces = [factory.piece() for _ in range(num_pieces)]

        self.metadata_id = m['ut_metadata']
        self.state['metadata_handshake'] = True


    def handle_metadata_piece(self, payload):
        # Split into metadata and bytes
        i = payload.index(b'ee') + 2
        metadata = dict(bencode.bdecode(payload[1:i]).items())

        # Validate metadata
        if any(key not in metadata for key in ['msg_type', 'piece']):
            self.disconnect()

        self.piece_index = metadata['piece']
        piece = config.manager.pieces[self.piece_index]
        if metadata['msg_type'] == 1 and not piece['complete']:
            piece['value'] = payload[i:]
            piece['complete'] = True
            self.printf('\033[92m𝑖\033[0m', iteration=self.piece_index)
        self.piece_index = -1


    def handle_have(self, payload):
        i = struct.unpack('>I', payload)[0]
        config.manager.has(self.address, i)


    def handle_bitfield(self, payload):
        bit_array = list(bitstring.BitArray(payload))
        for i, available in enumerate(bit_array):
            if available:
                config.manager.has(self.address, i)


    def handle_block(self, payload):
        # Split into metadata and bytes
        i, offset = struct.unpack('>II', payload[:8])
        block = payload[8:]
        config.manager.push(self.address, i, offset, block)


    def send(self, message):
        if not message:
            self.disconnect()
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
                self.send(message)
                break


    def send_interested(self):
        message = struct.pack('>IB', 1, 2)
        self.send(message)


    def send_request(self):
        message = config.manager.next(self.address)
        self.send(message)


    def printf(self, message, iteration=None):
        if iteration is None:
            cli.printf('{}'.format(message), prefix=self.address[0])
        else:
            cli.printf('{} {}/{}'.format(message, iteration + 1, len(config.manager.pieces)), prefix=self.address[0])
