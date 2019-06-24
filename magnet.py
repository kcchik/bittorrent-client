import urllib.parse
import sys
import re

class Magnet():
    def __init__(self, url):
        regex = re.compile('magnet:.+$')
        if not regex.match(url):
            print('Not a magnet link')
            sys.exit()
        params = urllib.parse.parse_qs(url[8:])
        if not 'xt' in params or not 'tr' in params:
            print('Invalid magnet link')
            sys.exit()
        self.name = params['dn'][0]
        self.info_hash = bytes(bytearray.fromhex(params['xt'][0][9:]))
        self.announce = params['tr'][0]