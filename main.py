from torrent import Torrent
from tracker import Tracker
from manager import Manager

if __name__ == '__main__':
    path = 'torrents/Maquia - When the Promised Flower Blooms [BD 1080p x265 12bit].mkv.torrent'
    torrent = Torrent(path) # Parse torrent file
    tracker = Tracker(torrent) # Connect to tracker and get peers
    manager = Manager(tracker) # Connect to peers
    print('%i available peers' % len(manager.peers))
    print('Connecting...')
    manager.connect()
    print('Connected with %i peers' % len(manager.peers))
    manager.start()
    print('Handshaking...')
    manager.handshake()
