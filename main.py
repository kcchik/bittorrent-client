from torrent import Torrent
from tracker import Tracker
from manager import Manager
import sys

if __name__ == '__main__':
    path = [
        'torrents/(一般コミック)今日から俺は!! 全38巻.zip.torrent',
        'torrents/Attack on Titan - Shingeki no Kyojin 117 [MangaStream].torrent',
        'torrents/Yuragi_Sou_No_Yuuna_San_v16.rar.torrent',
        "torrents/[CrazySubs] Queen's Blade Unlimited - 1 (ReinForce) English Subs.srt.torrent",
        'torrents/[Galator] Maquia - When The Promised Flower Blooms (BD 1080p x264 10-bit FLAC) [5188F390].mkv.torrent',
        'torrents/asobi-ova.srt.torrent',
        'torrents/[CommieRaws] Star☆Twinkle Precure - 19 [0E788EF2].ass.torrent',
    ]
    torrent = Torrent(path[int(sys.argv[1])])
    print(torrent.name)
    print(torrent.comment)

    tracker = Tracker(torrent)
    tracker.announce()

    manager = Manager(tracker)
    manager.start()
    # ⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏