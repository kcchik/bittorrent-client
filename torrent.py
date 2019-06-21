import bencode
import sys
import re

import config

class Torrent:
    def __init__(self, path):
        regex = re.compile('.+.torrent$')
        if not regex.match(path):
            print('Not a .torrent file')
            sys.exit()
        with open(path, 'rb') as torrent:
            dict = bencode.bdecode(bytes(torrent.read()))
            self.announce = dict['announce']
            self.info = dict['info']
