import socket
from bitstring import BitArray

class Peer:
    def __init__(self, address, num_pieces):
        self.address = address
        self.socket = socket.socket()
        self.socket.settimeout(5)
        self.bitfield = [False] * num_pieces
        self.state = {
            'choked': True,
            'handshake': False,
        }

    def connect(self):
        try:
            self.socket.connect(self.address)
            return True
        except OSError as e:
            return False

    def handshake(self, tracker):
        pstr = b'BitTorrent protocol'
        pstrlen = bytes([len(pstr)])
        reserved = b'\x00' * 8
        handshake = pstrlen + pstr + reserved + tracker.info_hash + tracker.peer_id.encode('iso-8859-1')
        try:
            self.socket.send(handshake)
        except OSError as e:
            e

    def interested(self):
        try:
            self.socket.send()
        except OSError as e:
            e

    def parse(self, data):
        if self.state['handshake'] == False:
            pstrlen = data[0]
            pstr = data[1:pstrlen + 1]
            data = data[pstrlen + 1:]
            reserved = data[0:8]
            info_hash = data[8:28]
            peer_id = data[28:48]
            data = data[48:]
        while len(data) > 4:
            length = int.from_bytes(data[0:4], 'big')
            if length > 1:
                payload = data[5:length + 4]
            if length > 0:
                id = data[4]
                if id == 0:
                    self.handle_choke()
                if id == 1:
                    self.handle_unchoke()
                if id == 4:
                    self.handle_have(payload)
                if id == 5:
                    self.handle_bitfield(payload)
                if id == 6:
                    self.handle_request(payload[0:4], payload[4:8], payload[8:12])
                if id == 7:
                    self.handle_piece(payload[0:4], payload[4:8], payload[8:length])
                if id == 8:
                    self.handle_cancel(payload[0:4], payload[4:8], payload[8:12])
                if id == 9:
                    self.handle_port(payload)
            data = data[length + 4:]
        self.state['handshake'] = True

    def handle_choke(self):
        print('choke')

    def handle_unchoke(self):
        print('unchoke')

    def handle_have(self, index):
        print('have')
        self.bitfield[int.from_bytes(index, 'big')] = True

    def handle_bitfield(self, bitfield):
        print('bitfield')
        self.bitfield = list(BitArray(bitfield))[0:len(self.bitfield)]

    def handle_request(self, index, begin, length):
        print('request')

    def handle_piece(self, index, begin, block):
        print('piece')

    def handle_cancel(self, index, begin, length):
        print('cancel')

    def handle_port(self, port):
        print('port')