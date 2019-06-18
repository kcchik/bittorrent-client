import re
import os
import hashlib
import bencode

import config
from torrent import Torrent
from tracker import Tracker
from manager import Manager

if __name__ == '__main__':
    files = [file for file in os.listdir('tmp/') if re.compile('.+.torrent$').match(file)]
    for i, file in enumerate(files):
        print('%i\t%s' % (i, file))
    i = input('\ntorrent: ')
    path = 'tmp/' + files[int(i)]
    torrent = Torrent(path)
    print('\n' + torrent.comment)
    print(config.PIECE_LENGTH, [file['length'] for file in torrent.files])

    tracker = Tracker(torrent)
    tracker.info_hash = hashlib.sha1(bencode.bencode(torrent.info)).digest()
    tracker.announce(torrent.announce)

    manager = Manager(tracker)
    manager.start()
    # ⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏