import os
import sys
import requests
import bencode


class Tracker:
    def __init__(self, info_hash):
        self.info_hash = info_hash
        self.peer_id = b'--KOJI--' + os.urandom(12)
        self.addresses = []


    def announce(self, url):
        params = {
            'info_hash': self.info_hash,
            'peer_id': self.peer_id,
            'port': 6881,
        }
        response = requests.get(url=url, params=params)
        response = dict(bencode.bdecode(response.content).items())

        # Validate response
        if 'failure reason' in response:
            print('Failure reason:', response['failure reason'])
            sys.exit()
        if 'peers' not in response:
            print('Failure reason:', 'no peers')
            sys.exit()

        # Parse response to get peer addresses
        peers = [response['peers'][i:i + 6] for i in range(0, len(response['peers']), 6)]
        for peer in peers:
            ip = '.'.join(str(i) for i in peer[:4])
            port = int.from_bytes(peer[-2:], 'big')
            self.addresses.append((ip, port))
