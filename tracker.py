from bencode import bencode, bdecode
import hashlib
import requests

class Tracker:
    def __init__(self, torrent):
        self.torrent = torrent
        self.addresses = []
        self.params = {
            'info_hash': hashlib.sha1(bencode(torrent.info)).digest(),
            'peer_id': '-KOJI-imatesttorrent',
            'event': 'started',
            'uploaded': 0,
            'downloaded': 0,
            'left': torrent.length,
        }

    def announce(self):
        response = requests.get(url=self.torrent.announce, params=self.params)
        response = bdecode(response.content)
        for key, value in response.items():
            if key == 'peers':
                peers = value
            if key == 'failure reason':
                raise Exception(value)
        print(peers)
        # peers = b'@\xeba\xba\x00\x00yk\x00!\x9f\xff}:X\xe7\xa4\xcf~\xa5Us\xf5\\\xb4\xc6\xc3;F*\xd2\x14\xbe\xbeA\xf0\xdf\x84J\x90Uo'
        peers = [peers[i:i + 6] for i in range(0, len(peers), 6)] # split into 6 byte parts
        for peer in peers:
            ip = '.'.join(str(i) for i in peer[:4])
            port = int.from_bytes(peer[-2:], 'big')
            self.addresses.append((ip, port))
