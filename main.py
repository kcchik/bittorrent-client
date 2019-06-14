import re
import os

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

    tracker = Tracker(torrent)
    tracker.announce()

    manager = Manager(tracker)
    manager.start()
    # ⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏