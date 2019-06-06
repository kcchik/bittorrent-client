from torrent import Torrent
from tracker import Tracker
from manager import Manager

if __name__ == '__main__':
    path = 'torrents/[Galator] Maquia - When The Promised Flower Blooms (BD 1080p x264 10-bit FLAC) [5188F390].mkv.torrent'
    torrent = Torrent(path)
    print(torrent.comment)

    tracker = Tracker(torrent)
    tracker.announce()

    manager = Manager(tracker)
    manager.start()
