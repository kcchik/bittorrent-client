from bencode import bencode, bdecode
import hashlib
import requests

class Tracker:
    def __init__(self, torrent):
        self.torrent = torrent
        self.addresses = []
        self.params = {
            'info_hash': hashlib.sha1(bencode(torrent.info)).digest(),
            'peer_id': '-KOJI-20725745207257',
            'event': 'started',
            'uploaded': 0,
            'downloaded': 0,
            'left': torrent.length,
        }

    def announce(self):
        # response = requests.get(url=self.torrent.announce, params=self.params)
        # response = bdecode(response.content)
        # print(response)
        # for key, value in response.items():
        #     if key == 'peers':
        #         peers = value
        #     if key == 'failure reason':
        #         raise Exception(value)
        peers = b"\x05\x87\xa2\x92\x87\x07\x05\xa4\xd8\x94k\xa0\x18\xb9\x81\xfa\xe3\x14.\xf6{F\xccU>\xd2\xdcg\xc8\xd5@\xeba\xba\x00\x00P\xd8T\xe6#'Q\x11\x18\xcah\xe6U\xe2\x7f\xfc#Z_\xd3\xf8\x1e\x81\x85`\xf8&\xc7\x1a\xe1c\\Hx\x1a\xe1m\xfc5\xea\xdf\x0cn6\xf8\xe8\xad\xb7\xad\xef\xe8.#'\xad\xf4$P\x1a\xe1\xb9\x15\xd9M\xd4t\xb9-\xc3\xc5N\x90\xb9\x95ZT\xc79"
        peers = [peers[i:i + 6] for i in range(0, len(peers), 6)] # split into 6 byte parts
        for peer in peers:
            ip = '.'.join(str(i) for i in peer[:4])
            port = int.from_bytes(peer[-2:], 'big')
            self.addresses.append((ip, port))
