from threading import Thread
from peer import Peer

class Manager(Thread):
    def __init__(self, tracker):
        Thread.__init__(self)
        self.tracker = tracker
        self.peers = [Peer(address) for address in tracker.addresses]

    def run(self):
        while True:
            for peer in self.peers:
                data = self.receive(peer.socket)
                if not data:
                    self.remove(peer)
                    print('No data')
                    continue
                print(repr(data))

    def receive(self, socket):
        data = b''
        while True:
            try:
                print('Waiting for packet')
                packet = socket.recv(4096)
                print('Received packet.')
                print(repr(packet))
                if len(packet) == 0:
                    break
                data += packet
            except OSError as e:
                print(e)
                break
        return data

    def connect(self):
        for peer in self.peers:
            if not peer.connect():
                self.remove(peer)

    def handshake(self):
        for peer in self.peers:
            handshake = peer.handshake(self.tracker)
            if not handshake:
                self.remove(peer)

    def remove(self, peer):
        peer.socket.close()
        self.peers.remove(peer)
