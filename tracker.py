import hashlib
import bencode
import requests
import os

class Tracker:
    def __init__(self, torrent):
        self.torrent = torrent
        self.info_hash = b''
        self.peer_id = b'--KOJI--' + os.urandom(12)
        self.addresses = []

    def announce(self, url):
        params = {
            'info_hash': self.info_hash,
            'peer_id': self.peer_id,
            'event': 'started',
            'uploaded': 0,
            'downloaded': 0,
        }
        response = requests.get(url=url, params=params)
        response = bencode.bdecode(response.content)
        for key, value in response.items():
            if key == 'peers':
                peers = value
            if key == 'failure reason':
                raise Exception(value)
        peers = [peers[i:i + 6] for i in range(0, len(peers), 6)]
        for peer in peers:
            ip = '.'.join(str(i) for i in peer[:4])
            port = int.from_bytes(peer[-2:], 'big')
            self.addresses.append((ip, port))
