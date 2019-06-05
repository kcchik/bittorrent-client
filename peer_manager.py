from threading import Thread
from peer import Peer

class PeerManager(Thread):
    def __init__(self, tracker):
        Thread.__init__(self)
        self.tracker = tracker
        self.peers = [Peer(address, tracker.num_pieces) for address in tracker.addresses]

    def run(self):
        while True:
            for peer in self.peers:
                data = self.receive(peer.socket)
                if not data:
                    self.remove(peer)
                    continue
                peer.parse(data)
                if peer.state['choking']:
                    peer.interested()

    def receive(self, socket):
        data = b''
        while True:
            try:
                packet = socket.recv(4096)
                if len(packet) == 0:
                    break
                data += packet
            except OSError as e:
                break
        return data

    def connect(self):
        for peer in self.peers:
            if not peer.connect():
                self.remove(peer)

    def handshake(self):
        for peer in self.peers:
            peer.handshake(self.tracker)

    def remove(self, peer):
        peer.socket.close()
        self.peers.remove(peer)
