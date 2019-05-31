from torrent import Torrent
from tracker import Tracker
from manager import Manager

if __name__ == '__main__':
    path = 'torrents/(一般コミック)今日から俺は!! 全38巻.zip.torrent'
    torrent = Torrent(path) # Parse torrent file
    tracker = Tracker(torrent) # Connect to tracker and get peers
    manager = Manager(tracker) # Connect to peers
    print('Connecting...')
    manager.connect()
    print('Connected with %i peers' % len(manager.peers))
    manager.start()
    print('Handshaking...')
    manager.handshake()
