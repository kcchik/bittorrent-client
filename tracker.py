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
        # peers = b'\xda\xdeg\x0b\xcf\x11=\x15\xfc\xf1\xc4j\xb4\t\x0c\x9f\xcb\xf7\xb46M\xfb\x1e>\xaf\x84M\xefx\xb1~,\xd2\xde\xf4\xbdz\x14P\xa3`\xe2j\xb5U\x98\xb6\x97\xaf\xb1)\x1f\xc8\xd5*\x91f\x89|9\xdb\xcfRr\x04n}\xc6\xb5\x93\xa0x~#\x11m\xaak~"\n\xd2\xd9\xf2\x0e\t\xd0\x80\xc4\'\xaf\xb1)\x1f\xc8\xd5\xaf\xb1)\x1f\xc8\xd5\x83\x81\xbed\xc8\xd5\xaf\xb1)\x1f\xc8\xd5~\x99]\x11\xf6\x18v\x00\xf3!IW~nU\xa8c\x95}\xc6\xb5\x93\xa0x|\x9b:\xea`Ez\x12\xd6\xa56\x84*\x7f\xc8\xea\x9c\xb2q\x93\x00\x89g\xdbz\xd1|\xe1\xce\xc0\x956\xf5\x8b\x7f|r\xa2Cwnu@\xeba\xba\x00\x00\x01\xa5\xbc\x91S\xfb\xdb\xcfRr\x04n\xaf\xb1)\x1f\xc8\xd5}\xc6\xb5\x93\xa0xz\xd1|\xe1\xce\xc0\xca\xd8Tk\\]\x83\x81\xbed\xc8\xd5\xdb\xcfRr\x04nv\x00\xf3!IW\xdbb\xd9*\xc8\xd5v\x00\xf3!IW\xaf\x84M\xefx\xb1z\xd1|\xe1\xce\xc0~"\n\xd2\xd9\xf2\x01\xa5\xbc\x91S\xfb\xaf\x84M\xefx\xb1\xdbb\xd9*\xc8\xd5\xd9\xb2Z7:\xbc}\xc4\x80\x00\xe7\xef'
        peers = [peers[i:i + 6] for i in range(0, len(peers), 6)] # split into 6 byte parts
        for peer in peers:
            ip = '.'.join(str(i) for i in peer[:4])
            port = int.from_bytes(peer[-2:], 'big')
            self.addresses.append((ip, port))
