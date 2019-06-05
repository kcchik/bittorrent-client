from bencode import bdecode

class Torrent:
    def __init__(self, path):
        file = open(path, 'rb')
        content = file.read() # Raw contents
        content = bytes(content) # ISO-8859-1 encoding (\x__)
        dict = bdecode(content) # Decode into dictionary
        self.announce = dict['announce']
        self.comment = dict['comment']
        self.info = dict['info']
