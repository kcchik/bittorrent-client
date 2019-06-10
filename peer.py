from threading import Thread, active_count
from struct import pack, unpack
from bitstring import BitArray
import socket
import config
import hashlib

class Peer(Thread):
    def __init__(self, id, manager, address):
        Thread.__init__(self)
        self.id = id
        self.manager = manager
        self.address = address
        self.socket = socket.socket()
        socket.timeout(10)
        self.has = [False] * len(manager.pieces)
        self.state = {
            'choking': True,
            'handshake': False,
        }
        self.peer_id = b''

    def connect(self):
        try:
            self.socket.connect(self.address)
            print('connected', self.address[0])
            return True
        except OSError as e:
            return False

    def run(self):
        if not self.connect():
            return
        self.send_handshake()
        while True:
            message = self.receive()
            if not message:
                print('no message', self.address[0], self.peer_id)
                return
            if not self.parse(message):
                return

            if self.state['choking']:
                self.send_interested()
            else:
                i = self.next_available_piece_index()
                if i < 0:
                    return
                self.send_request(i)

            if self.manager.complete():
                self.manager.write()

    def receive(self):
        message = b''
        while True:
            try:
                print('receiving', self.address[0])
                packet = self.socket.recv(4096)
            except OSError as e: # does thread die here
                print('receive', e)
                break
            if not packet:
                break
            message += packet
        return message

    def parse(self, data):
        if not self.state['handshake']:
            pstrlen = data[0]
            pstr, reserved, info_hash, self.peer_id = unpack('>{}s8s20s20s'.format(pstrlen), data[1:pstrlen + 49])
            data = data[pstrlen + 49:]
            if not info_hash == self.manager.tracker.params['info_hash']:
                print('failed handshake', self.address[0])
                return False
            print('handshake recv', self.address[0], self.peer_id)
        while len(data) > 4:
            length = unpack('>I', data[0:4])[0]
            if length > 1:
                payload = data[5:length + 4]
            if length > 0:
                type = data[4]
                if type == 0 or type == 1:
                    self.state['choking'] = not bool(type)
                if type == 4:
                    self.handle_have(payload)
                if type == 5:
                    self.handle_bitfield(payload)
                if type == 7:
                    self.handle_block(length, payload)
            data = data[length + 4:]
        self.state['handshake'] = True
        return True

    def handle_have(self, payload):
        i = unpack('>I', payload)[0]
        self.has[i] = True
        self.manager.pieces[i].state['available'] = True

    def handle_bitfield(self, bitfield):
        for i, available in enumerate(list(BitArray(bitfield))[0:len(self.has)]):
            self.has[i] = available
            self.manager.pieces[i].state['available'] = True

    def handle_block(self, length, payload):
        i, offset = unpack('>II', payload[0:8])
        block = payload[8:]
        piece = self.manager.pieces[i]
        piece.blocks[int(offset / config.BLOCK_SIZE)] = block
        print('block (%i/%i) (%i/%i)' % (int(offset / config.BLOCK_SIZE), len(piece.blocks), i, len(self.manager.pieces)), self.peer_id)
        if piece.left() == 0:
            if hashlib.sha1(piece.data()).digest() == self.manager.tracker.torrent.pieces[i]:
                print('piece complete', i, self.peer_id)
                piece.state['complete'] = True
            else:
                print('piece incomplete', i, self.peer_id)
                piece.blocks = [None] * len(piece.blocks)
                piece.state['requesting'] = None
                self.has[i] = False

    def send(self, message):
        try:
            self.socket.send(message)
        except OSError as e:
            print('send', e)
            return

    def send_handshake(self):
        pstr = b'BitTorrent protocol'
        pstrlen = bytes([len(pstr)])
        reserved = b'\x00' * 8
        message = pstrlen + pstr + reserved + self.manager.tracker.params['info_hash'] + self.manager.tracker.params['peer_id'].encode('iso-8859-1')
        print('handshake send', self.address[0])
        self.send(message)

    def send_interested(self):
        message = pack('>IB', 1, 2)
        print('interested', self.peer_id)
        self.send(message)

    def send_request(self, i):
        piece = self.manager.pieces[i]
        piece.state['requesting'] = self.id
        offset = (len(piece.blocks) - piece.left()) * config.BLOCK_SIZE
        message = pack('>IBIII', 13, 6, i, offset, config.BLOCK_SIZE)
        print('request (%i/%i) (%i/%i)' % (len(piece.blocks) - piece.left(), len(piece.blocks), i, len(self.manager.pieces)), self.peer_id)
        self.send(message)

    def next_available_piece_index(self):
        for i, piece in enumerate(self.manager.pieces):
            if not piece.state['complete'] and (not piece.state['requesting'] or piece.state['requesting'] == self.id) and self.has[i]:
                return i
        else:
            return -1