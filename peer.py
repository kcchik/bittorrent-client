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
        self.piece = None
        self.state = {
            'choking': True,
            'handshake': False,
        }

    def connect(self):
        try:
            self.socket.connect(self.address)
            self.printo('connected')
            return True
        except OSError as e:
            return False

    def run(self):
        if not self.connect():
            return
        self.send_handshake()

        messages = b''
        while True:
            try:
                packet = self.socket.recv(4096)
            except OSError as e:
                self.printo('disconnecting %s' % e)
                if self.piece:
                    self.piece.state['requesting'] = None
                return

            if len(packet) and not self.state['handshake']:
                packet = self.handle_handshake(packet)

            messages += packet
            while len(messages) >= 4:
                length = unpack('>I', messages[0:4])[0]
                if length == 0 or len(messages) < length + 4:
                    break
                message = messages[4:length + 4]
                # self.printo('message %s' % message)
                self.handle(message)
                messages = messages[length + 4:]

            if self.state['choking']:
                self.send_interested()
            else:
                i = self.next_available_piece_index()
                if i >= 0:
                    self.send_request(i)

            if self.manager.complete():
                self.manager.write()

    def handle(self, message):
        type = message[0]
        payload = b''
        if len(message) > 1:
            payload = message[1:]
        if type == 0:
            self.state['choking'] = True
            self.printo('choked')
        if type == 1:
            self.state['choking'] = False
            self.printo('unchoked')
        if type == 4:
            self.handle_have(payload)
        if type == 5:
            self.handle_bitfield(payload)
        if type == 7:
            self.handle_block(payload)

    def handle_handshake(self, packet):
        pstrlen = packet[0]
        pstr, reserved, info_hash, peer_id = unpack('>{}s8s20s20s'.format(pstrlen), packet[1:pstrlen + 49])
        if not info_hash == self.manager.tracker.params['info_hash']:
            self.printo('handshake failed')
            return b''
        self.printo('handshake received')
        self.state['handshake'] = True
        return packet[pstrlen + 49:]

    def handle_have(self, payload):
        i = unpack('>I', payload)[0]
        self.has[i] = True
        self.manager.pieces[i].state['available'] = True

    def handle_bitfield(self, payload):
        for i, available in enumerate(list(BitArray(payload))[0:len(self.has)]):
            self.has[i] = available
            self.manager.pieces[i].state['available'] = True

    def handle_block(self, payload):
        i, offset = unpack('>II', payload[0:8])
        if not self.piece == self.manager.pieces[i]:
            return
        block = payload[8:]
        self.piece.blocks[int(offset / config.BLOCK_SIZE)] = block
        self.printo('receive (%i/%i) (%i/%i)' % (int(offset / config.BLOCK_SIZE) + 1, len(self.piece.blocks), i + 1, len(self.manager.pieces)))
        if self.piece.left() == 0:
            if hashlib.sha1(self.piece.data()).digest() == self.manager.tracker.torrent.pieces[i]:
                self.printo('piece complete %i' % i)
                self.piece.state['complete'] = True
            else:
                self.printo('piece incomplete %i' % i)
                self.piece.blocks = [None] * len(self.piece.blocks)
                self.piece.state['requesting'] = None
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
        message = pstrlen + pstr + reserved + self.manager.tracker.params['info_hash'] + self.manager.tracker.params['peer_id'].encode('iso-8859-1')
        # self.printo('handshake sent')
        self.send(message)

    def send_interested(self):
        message = pack('>IB', 1, 2)
        # self.printo('interested')
        self.send(message)

    def send_request(self, i):
        self.piece = self.manager.pieces[i]
        self.piece.state['requesting'] = self.id
        offset = (len(self.piece.blocks) - self.piece.left()) * config.BLOCK_SIZE
        message = pack('>IBIII', 13, 6, i, offset, config.BLOCK_SIZE)
        # self.printo('request (%i/%i) (%i/%i)' % (len(self.piece.blocks) - self.piece.left() + 1, len(self.piece.blocks), i + 1, len(self.manager.pieces)))
        self.send(message)

    def next_available_piece_index(self):
        for i, piece in enumerate(self.manager.pieces):
            if not piece.state['complete'] and (not piece.state['requesting'] or piece == self.piece) and self.has[i]:
                return i
        else:
            return -1

    def printo(self, message):
        print(self.address[0].ljust(20), message)