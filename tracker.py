from bencode import bencode, bdecode
import hashlib
import requests

class Tracker:
    def __init__(self, torrent):
        self.num_pieces = int(len(torrent.info['pieces']) / 20)
        self.info_hash = hashlib.sha1(bencode(torrent.info)).digest()
        self.peer_id = '-KOJI-20725745207257'
        params = {
            'info_hash': self.info_hash,
            'peer_id': self.peer_id,
            'event': 'started',
            'uploaded': 0,
            'downloaded': 0,
            'left': torrent.info['length'],
        }
        response = requests.get(url=torrent.announce, params=params)
        response = bdecode(response.content)
        for key, value in response.items():
            if key == 'peers':
                peers = value
            if key == 'failure reason':
                raise Exception(value)
        peers = [peers[i:i + 6] for i in range(0, len(peers), 6)] # Split 6 byte parts
        self.addresses = []
        for peer in peers:
            ip = '.'.join(str(b) for b in peer[:4])
            port = int.from_bytes(peer[-2:], 'big')
            self.addresses.append((ip, port))