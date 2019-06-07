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
        response = requests.get(url=self.torrent.announce, params=self.params)
        response = bdecode(response.content)
        print(response)
        for key, value in response.items():
            if key == 'peers':
                peers = value
            if key == 'failure reason':
                raise Exception(value)
        # peers = b"yj\x86\x1dB~:\x01\xb2;\x95\xe7<ib\xad\xe0\xc3~\xa3\xad\xdf\xfb\xf8\xd3\x01\xd6\x17l\x0f\x85\xcf\x80\xa0Z\x0b~\\\xc5\r\x83\x0f\x0e\t\x05`7\x83<c@\xdd]\xf1\xd3\x01\xce\xa2X\xdcv\xedI\xf6S]1\xfde\x85O\xd1|\xdb\xda\x031\x8a\x0e\x08\x83\x00\x82\xda\xcb\x8b^z\xcc\x9e</,-\xed\xe1\x0e\r\xe7\xa0\xf1\xcd\x85\xcf\x80\xa0Z\x0be7\x9e[\x86\x93t'\x1e'\xe5>\xcb\x87\xcb\xb8k\xb7=\xc1\xd9\x85m\xf6\x85\xc9\xc3\xc0V\xe2|\xd2\x10\xe42\xb2\x99\xce}L\xdf\xdfRf\x1ck\xcc\xe3\x85{t1\x96zv\xedI\xf6S]<)p\x1e\x8bO|\xd2\x10\xe42\xb2\xdd\xbb\x15\\\x87\xe7vh]\x10\xa9T=\xc1\xd9\x85m\xf6wh-\xe2\xdf\xfe\x1bi\xed\x13)8\xdd\xbb\x15\\\x87\xe7~\\\xc5\r\x83\x0f\xdbn\xd0'\x9b\xb5t\xfd\x8fR9\x07\x9d\xc0\xe9\xacX\x85\xb9\xc68\xa7\xc8\xd5\x99\xe8\xa4\x82q\xab~\xdbn\xe0W\xddz\x878\xcd?K_\xd3Z\x8e\xee\xa6~\xd1\xc04N\xaf~\xf3EW\xaf\xdb\xb48c'N(tF\xcc\x91\xc8\xd5\x85{t1\x96z"
        peers = [peers[i:i + 6] for i in range(0, len(peers), 6)] # split into 6 byte parts
        for peer in peers:
            ip = '.'.join(str(i) for i in peer[:4])
            port = int.from_bytes(peer[-2:], 'big')
            self.addresses.append((ip, port))
