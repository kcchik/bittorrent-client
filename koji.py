from bencode import bencode, bdecode
import hashlib
import requests
import socket

ENCODING = 'ISO-8859-1'

torrent = 'torrents/Maquia - When the Promised Flower Blooms [BD 1080p x265 12bit].mkv.torrent'
file = open(torrent, 'rb')
content = file.read() # Raw contents
content = bytes(content) # ISO-8859-1 encoding (\x__)
dict = bdecode(content) # Decode into dictionary

announce = dict['announce']
info = dict['info']
length = info['length']

info_encoded = bencode(info)
info_hash = hashlib.sha1(info_encoded).digest()
peer_id = 'koji2072574520725745'
params = {
    'info_hash': info_hash,
    'peer_id': peer_id,
    'event': 'started',
    'uploaded': 0,
    'downloaded': 0,
    'left': length,
}
response = requests.get(url=announce, params=params)
response = bdecode(response.content)
print('Response: ', response)

response = [
    ('complete', 18),
    ('downloaded', 496),
    ('incomplete', 2),
    ('interval', 1810),
    ('peers', b"@\xeba\xba\x00\x00O\xa6\xf9\x92F\xcfQ\x11\x18\xcah\xe6U\xe2\x7f\xfc#ZYMs#\x1eaY\x86\xa4l#'_\xd3\xf8\x1e\x81\x85c\\Hx\x1a\xe1m\xfc5\xea\xf4'q\xbe\xe8\x13\xa8)\xa2\xdc\xa2\n#'\xaa\xe7\xbb\x03\xc2l\xad\xef\xe8.#'\xb0('\x8e\xc0\x08\xb5+?:\xd2o\xb5\xa9\x1b\x1d#'\xb9\x15\xd9M\xd8\xef\xb9-\xc3\xc5N\x90\xb9\x95ZT\xc79\xde\xfc*.#'"),
    ('peers6', '')
]

for key, value in response:
    if key == 'peers':
        peers = value
    if key == 'failure reason':
        raise Exception(value)

num = 1
peers = [peers[i:i + 6] for i in range(0, len(peers), 6)] # Split 6 byte parts
ip = '.'.join(str(i) for i in peers[num][:4])
# ip = str(int.from_bytes(peers[0][:4], 'big'))
port = int.from_bytes(peers[num][-2:], 'big')

print('Peer: ', peers[num])
print('IP: ', ip)
print('Port: ', port)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((ip, port))

pstr = b'BitTorrent protocol'
pstrlen = bytes([len(pstr)])
reserved = b'\x00' * 8
handshake = pstrlen + pstr + reserved + info_hash + peer_id.encode(ENCODING)
print('Handshake 1: ', handshake)
sock.send(handshake)
data = sock.recv(1024)
sock.close()
print('Handshake 2: ', repr(data))
