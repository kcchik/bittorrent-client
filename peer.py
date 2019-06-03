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
        print('Handshake: ', handshake)
        try:
            self.socket.send(handshake)
        except OSError as e:
            print('Failed to handshake: ', e)
