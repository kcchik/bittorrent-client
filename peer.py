import socket

class Peer:
    def __init__(self, address):
        self.address = address
        self.socket = socket.socket()
        self.socket.settimeout(5)

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
            print('Handshake success')
        except OSError as e:
            print('Handshake failure')

    def parse(self, data):
        # print('From %s: ' % self.address[0], data)
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
                    self.choke()
                if id == 1:
                    self.unchoke()
                if id == 2:
                    self.interested()
                if id == 3:
                    self.not_interested()
                if id == 4:
                    self.have(payload)
                if id == 5:
                    self.bitfield(payload)
                if id == 6:
                    self.request(payload[0:4], payload[4:8], payload[8:12])
                if id == 7:
                    self.piece(payload[0:4], payload[4:8], payload[8:length])
                if id == 8:
                    self.cancel(payload[0:4], payload[4:8], payload[8:12])
                if id == 9:
                    self.port(payload)
            data = data[length + 4:]

    def choke(self):
        print('choke')

    def unchoke(self):
        print('unchoke')

    def interested(self):
        print('interested')

    def not_interested(self):
        print('not interested')

    def have(self, index):
        print('have')

    def bitfield(self, bitfield):
        print('bitfield')

    def request(self, index, begin, length):
        print('request')

    def piece(self, index, begin, block):
        print('piece')

    def cancel(self, index, begin, length):
        print('cancel')

    def port(self, port):
        print('port')