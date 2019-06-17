import re
import os

import config
from torrent import Torrent
from tracker import Tracker
from manager import Manager

if __name__ == '__main__':
    files = [file for file in os.listdir('torrents/') if re.compile('.+.torrent$').match(file)]
    for i, file in enumerate(files):
        print('%i\t%s' % (i, file))
    path = input('\ntorrent: ')
    torrent = Torrent('torrents/' + files[int(path)])
    print('\n' + torrent.comment)
    print(config.PIECE_LENGTH, torrent.files)

    # tracker = Tracker(torrent)
    # tracker.announce()

    # manager = Manager(tracker)
    # manager.start()
    # ⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏