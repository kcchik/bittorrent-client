from torrent import Torrent
from tracker import Tracker
from manager import Manager
from os import listdir
import sys

if __name__ == '__main__':
    files = [file for file in listdir('torrents/') if file != '.DS_Store']
    for i, file in enumerate(files):
        print('%i\t%s' % (i, file))
    path = input()
    torrent = Torrent('torrents/' + files[int(path)])
    print(torrent.name)
    print(torrent.comment)

    tracker = Tracker(torrent)
    tracker.announce()

    manager = Manager(tracker)
    manager.start()
    # ⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏