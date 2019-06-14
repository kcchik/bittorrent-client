import hashlib
import bencode
import requests
import os

class Tracker:
    def __init__(self, torrent):
        self.torrent = torrent
        self.addresses = []
        self.params = {
            'info_hash': hashlib.sha1(bencode.bencode(torrent.info)).digest(),
            'peer_id': b'--KOJI--' + os.urandom(12),
            'event': 'started',
            'uploaded': 0,
            'downloaded': 0,
            'left': torrent.length,
        }

    def announce(self):
        response = requests.get(url=self.torrent.announce, params=self.params)
        response = bencode.bdecode(response.content)
        for key, value in response.items():
            if key == 'peers':
                peers = value
            if key == 'failure reason':
                raise Exception(value)
        peers = [peers[i:i + 6] for i in range(0, len(peers), 6)] # split into 6 byte parts
        for peer in peers:
            ip = '.'.join(str(i) for i in peer[:4])
            port = int.from_bytes(peer[-2:], 'big')
            self.addresses.append((ip, port))
