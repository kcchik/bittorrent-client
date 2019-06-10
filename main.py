from torrent import Torrent
from tracker import Tracker
from manager import Manager

if __name__ == '__main__':
    path = 'torrents/(一般コミック)今日から俺は!! 全38巻.zip.torrent'
    torrent = Torrent(path)
    print(torrent.comment)

    tracker = Tracker(torrent)
    tracker.announce()

    manager = Manager(tracker)
    manager.start()
    # ⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏