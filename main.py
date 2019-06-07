from torrent import Torrent
from tracker import Tracker
from manager import Manager

if __name__ == '__main__':
    path = 'torrents/Yuragi_Sou_No_Yuuna_San_v16.rar.torrent'
    torrent = Torrent(path)
    print(torrent.comment)

    tracker = Tracker(torrent)
    tracker.announce()

    manager = Manager(tracker)
    manager.start()
    # ⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏