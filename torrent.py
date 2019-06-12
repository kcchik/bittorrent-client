from bencode import bdecode

class Torrent:
    def __init__(self, path):
        try:
            file = open(path, 'rb')
        except Exception as e:
            print(e)
            return
        dict = bdecode(bytes(file.read()))
        self.announce = dict['announce']
        self.comment = dict['comment']
        self.info = dict['info']
        self.name = self.info['name']
        self.pieces = [self.info['pieces'][i:i + 20] for i in range(0, len(self.info['pieces']), 20)]
        self.piece_length = self.info['piece length']
        # self.files = []
        # if self.info['files']:
        #     self.length = 0
        #     for file in self.info['files']:
        #         self.length += file['length']
        #         self.files.append({
        #             length: file['length'],
        #             path: file['path'],
        #         })
        # else:
        self.length = self.info['length']
        file.close()
