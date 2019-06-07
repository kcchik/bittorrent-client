from bencode import bdecode

class Torrent:
    def __init__(self, path):
        try:
            file = open(path, 'rb')
        except Error as e:
            print(e)
        dict = bdecode(bytes(file.read()))
        self.announce = dict['announce']
        self.comment = dict['comment']
        self.info = dict['info']
        self.name = self.info['name']
        self.pieces = [self.info['pieces'][i:i + 20] for i in range(0, len(self.info['pieces']), 20)]
        self.piece_length = self.info['piece length']
        self.length = self.info['length']
        file.close()
