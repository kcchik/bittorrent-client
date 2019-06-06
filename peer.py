from threading import Thread
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
        self.pieces = manager.tracker.torrent.pieces

        self.socket = socket.socket()
        self.socket.settimeout(10)
        self.has = [False] * len(self.pieces)
        self.state = {
            'choking': True,
            'handshake': False,
        }

    def connect(self):
        try:
            self.socket.connect(self.address)
            print('connected: ', self.address[0])
            return True
        except OSError as e:
            return False

    def run(self):
        if not self.connect():
            return
        self.handshake()
        while True:
            message = self.receive()
            if not message:
                return
            self.parse(message)

            if self.state['choking']:
                self.interested()
            else:
                self.request()

    def receive(self):
        message = b''
        while True:
            try:
                packet = self.socket.recv(4096)
            except OSError as e:
                break
            if not packet:
                break
            message += packet
        return message

    def parse(self, data):
        if not self.state['handshake']:
            pstrlen = data[0]
            pstr, reserved, info_hash, peer_id = unpack('>{}s8s20s20s'.format(pstrlen), data[1:pstrlen + 49])
            data = data[pstrlen + 49:]
        while len(data) > 4:
            length = unpack('>I', data[0:4])[0]
            if length > 1:
                payload = data[5:length + 4]
            if length > 0:
                type = data[4]
                if type == 0 or type == 1:
                    self.state['choking'] = not bool(type)
                if type == 4:
                    self.have(payload)
                if type == 5:
                    self.bitfield(payload)
                if type == 7:
                    self.piece(length, payload)
            data = data[length + 4:]
        self.state['handshake'] = True

    def send(self, message):
        try:
            self.socket.send(message)
        except OSError as e:
            return

    def handshake(self):
        pstr = b'BitTorrent protocol'
        pstrlen = bytes([len(pstr)])
        reserved = b'\x00' * 8
        message = pstrlen + pstr + reserved + self.manager.tracker.params['info_hash'] + self.manager.tracker.params['peer_id'].encode('iso-8859-1')
        self.send(message)

    def interested(self):
        message = pack('>IB', 1, 2)
        self.send(message)

    def request(self):
        # \x00\x00\x00\r
        # \x06
        # \x00\x00\x00\x00
        # \x00\x00\x00\x00
        # \x00\x00@\x00
        for i, available in enumerate(self.has):
            piece = self.manager.pieces[i]
            if available and not piece.done:
                offset = i * config.BLOCK_SIZE
                break
        else:
            return
        message = pack('>IBIII', 13, 6, i, offset, config.BLOCK_SIZE)
        print('request: ', message)
        self.send(message)

    def have(self, payload):
        i = unpack('>I', payload)[0]
        self.has[i] = True

    def bitfield(self, bitfield):
        for i, available in enumerate(list(BitArray(bitfield))[0:len(self.has)]):
            self.has[i] = available

    def piece(self, length, payload):
        print('piece: ', len(payload))
        i, offset, block = unpack('>II{}s'.format(length - 9), payload)
        piece = self.manager.pieces[i]
        piece.blocks[int(offset / config.BLOCK_SIZE)] = block
        if piece.complete and hashlib.sha1(piece.data()).digest() == self.pieces[i]:
            print('got piece')
            piece.done = True
