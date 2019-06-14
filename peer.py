from threading import Thread, active_count
from struct import pack, unpack
from bitstring import BitArray
import socket
import config
import hashlib

class Peer(Thread):
    def __init__(self, manager, address):
        Thread.__init__(self)
        self.manager = manager
        self.address = address
        self.socket = socket.socket()
        self.socket.settimeout(10)
        self.has = [False] * len(manager.pieces)
        self.piece = None
        self.piece_i = -1
        self.choking = True
        self.handshake = False

    def connect(self):
        try:
            self.socket.connect(self.address)
            self.printo('connected')
            return True
        except OSError as e:
            return False

    def disconnect(self):
        if self.piece:
            self.piece.requesting = False
        self.socket.close()

    def run(self):
        if not self.connect():
            return
        self.send_handshake()

        messages = b''
        while True:
            try:
                packet = self.socket.recv(4096)
            except OSError as e:
                self.printo('disconnected (%s)' % e)
                self.disconnect()
                return

            if len(packet) and not self.handshake:
                packet = self.handle_handshake(packet)

            if not len(packet):
                self.printo('disconnected (empty packet)')
                self.disconnect()
                return

            messages += packet
            while len(messages) >= 4:
                length = unpack('>I', messages[0:4])[0]
                if length == 0 or len(messages) < length + 4:
                    break
                message = messages[4:length + 4]
                self.handle(message)
                if self.choking:
                    self.send_interested()
                else:
                    if not self.piece:
                        self.find_piece()
                    if self.piece:
                        self.send_request()
                messages = messages[length + 4:]

    def handle(self, message):
        type = message[0]
        payload = b''
        if len(message) > 1:
            payload = message[1:]
        if type == 0:
            self.choking = True
        if type == 1:
            self.choking = False
        if type == 2:
            self.printo('interested')
        if type == 3:
            self.printo('uninsterested')
        if type == 4:
            self.handle_have(payload)
        if type == 5:
            self.handle_bitfield(payload)
        if type == 6:
            self.printo('request')
        if type == 7:
            self.handle_block(payload)
        if type == 8:
            self.printo('cancel')
        if type == 9:
            self.printo('port')


    def handle_handshake(self, packet):
        pstrlen = packet[0]
        pstr, reserved, info_hash, peer_id = unpack('>{}s8s20s20s'.format(pstrlen), packet[1:pstrlen + 49])
        if not info_hash == self.manager.tracker.params['info_hash']:
            return b''
        self.handshake = True
        return packet[pstrlen + 49:]

    def handle_have(self, payload):
        i = unpack('>I', payload)[0]
        self.has[i] = True

    def handle_bitfield(self, payload):
        for i, available in enumerate(list(BitArray(payload))[0:len(self.has)]):
            self.has[i] = available

    def handle_block(self, payload):
        i, offset = unpack('>II', payload[0:8])
        if not self.piece == self.manager.pieces[i]:
            return
        block = payload[8:]
        self.piece.blocks[offset // config.BLOCK_LENGTH] = block
        if self.piece.left() == 0:
            if hashlib.sha1(self.piece.data()).digest() == self.manager.tracker.torrent.pieces[i]:
                self.printo('complete (%i/%i)' % (i + 1, len(self.manager.pieces)))
                self.piece.complete = True
                self.piece = None
                self.manager.write()
            else:
                self.printo('failed (%i/%i)' % (i + 1, len(self.manager.pieces)))
                self.piece.blocks = [None] * len(self.piece.blocks)
                self.piece.requesting = False
                self.piece = None
                self.has[i] = False

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
        message = pack('>IB', 1, 2)
        self.send(message)

    def send_request(self):
        block_length = config.BLOCK_LENGTH
        if self.piece_i + 1 == len(self.manager.pieces) and self.piece.left() == 1:
            block_length = self.manager.tracker.torrent.length % config.BLOCK_LENGTH
        block_i = (len(self.piece.blocks) - self.piece.left()) * config.BLOCK_LENGTH
        message = pack('>IBIII', 13, 6, self.piece_i, block_i, block_length)
        self.send(message)

    def find_piece(self):
        for i, piece in enumerate(self.manager.pieces):
            if not piece.requesting and self.has[i]:
                piece.requesting = True
                self.piece = piece
                self.piece_i = i
                return

    def printo(self, message):
        print(self.address[0].ljust(20), message)