import re
import os

import config
from scraper import Scraper
from torrent import Torrent
from tracker import Tracker
from manager import Manager

if __name__ == '__main__':
    # scraper = Scraper()
    # query = input('query: ')
    # scraper.query(query)
    # scraper.search()
    files = [file for file in os.listdir('tmp/') if re.compile('.+.torrent$').match(file)]
    for i, file in enumerate(files):
        print('%i\t%s' % (i, file))
    path = input('\ntorrent: ')
    torrent = Torrent('tmp/' + files[int(path)])
    print('\n' + torrent.comment)
    print(config.PIECE_LENGTH, [file['length'] for file in torrent.files])

    tracker = Tracker(torrent)
    tracker.announce()

    manager = Manager(tracker)
    manager.start()
    # ⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏