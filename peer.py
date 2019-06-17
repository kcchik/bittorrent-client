import threading
import socket
import hashlib
import struct
import bitstring
import sys
import time

import config

class Peer(threading.Thread):
    def __init__(self, manager, address):
        threading.Thread.__init__(self)
        self.manager = manager
        self.address = address
        self.socket = socket.socket()
        self.socket.settimeout(10)
        self.handshake = False
        self.choking = True
        self.connected = True
        self.has = [False] * len(manager.pieces)
        self.piece = -1

    def connect(self):
        try:
            self.socket.connect(self.address)
        except OSError as e:
            self.disconnect()

    def disconnect(self):
        if self.piece != -1:
            self.manager.pieces[self.piece].requesting = False
        self.socket.close()
        self.connected = False
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

            if not self.handshake:
                packet = self.handle_handshake(packet)

            messages += packet
            while len(messages) >= 4:
                length = struct.unpack('>I', messages[:4])[0]
                if length == 0 or len(messages) < length + 4:
                    break
                message = messages[4:length + 4]
                self.handle(message)
                messages = messages[length + 4:]

    def handle(self, message):
        type = message[0]
        payload = b''
        if len(message) > 1:
            payload = message[1:]

        if type == 0:
            self.choking = True
        elif type == 1:
            self.choking = False
        elif type == 4:
            self.handle_have(payload)
        elif type == 5:
            self.handle_bitfield(payload)
        elif type == 7:
            self.handle_block(payload)

        if self.choking:
            self.send_interested()
        else:
            self.find_piece()

    def handle_handshake(self, packet):
        pstrlen = packet[0]
        info_hash = struct.unpack('>20s', packet[pstrlen + 9:pstrlen + 29])[0]
        if info_hash != self.manager.tracker.params['info_hash']:
            self.disconnect()
        self.handshake = True
        return packet[pstrlen + 49:]

    def handle_have(self, payload):
        i = struct.unpack('>I', payload)[0]
        self.has[i] = True

    def handle_bitfield(self, payload):
        for i, available in enumerate(list(bitstring.BitArray(payload))[:len(self.has)]):
            self.has[i] = available

    def handle_block(self, payload):
        i, offset = struct.unpack('>II', payload[:8])
        block = payload[8:]
        if self.piece != i:
            return
        piece = self.manager.pieces[i]
        piece.blocks[offset // config.BLOCK_LENGTH] = block
        if piece.left() == 0:
            if hashlib.sha1(piece.data()).digest() == piece.hash:
                self.printo('\033[92m✓\033[0m {}/{}'.format(i + 1, len(self.manager.pieces)))
                piece.complete = True
            else:
                self.printo('\033[91m✗\033[0m {}/{}'.format(i + 1, len(self.manager.pieces)))
                piece.blocks = [None] * len(piece.blocks)
                self.has[i] = False
            self.piece = -1
            piece.requesting = False

    def send(self, message):
        try:
            self.socket.send(message)
        except OSError as e:
            return

    def send_handshake(self):
        pstr = b'BitTorrent protocol'
        pstrlen = bytes([len(pstr)])
        reserved = b'\x00' * 8
        message = pstrlen + pstr + reserved + self.manager.tracker.params['info_hash'] + self.manager.tracker.params['peer_id']
        self.send(message)

    def send_interested(self):
        message = struct.pack('>IB', 1, 2)
        self.send(message)

    def send_request(self):
        piece = self.manager.pieces[self.piece]
        block_length = config.BLOCK_LENGTH
        if self.piece + 1 == len(self.manager.pieces) and piece.left() == 1:
            block_length = self.manager.tracker.torrent.length % config.BLOCK_LENGTH
        message = struct.pack('>IBIII', 13, 6, self.piece, piece.block_offset(), block_length)
        self.send(message)

    def find_piece(self):
        while self.piece == -1:
            for i, piece in enumerate(self.manager.pieces):
                if not piece.requesting and not piece.complete and self.has[i]:
                    piece.requesting = True
                    self.piece = i
                    break
            if not any(not file.complete for file in self.manager.files):
                self.disconnect()
            time.sleep(0.1)
        self.send_request()

    def printo(self, message):
        print(self.address[0].ljust(20), message)