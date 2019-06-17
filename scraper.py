import feedparser
import urllib.parse

# {
#   'title': '[Nemuri] Kōya no Kotobuki Hikōtai 荒野のコトブキ飛行隊 (2019-2019) Discography / Music Collection [4 CDs] [MP3]',
#   'title_detail': {
#       'type': 'text/plain',
#       'language': None,
#       'base': 'https://nyaa.si/?page=rss&',
#       'value': '[Nemuri] Kōya no Kotobuki Hikōtai 荒野のコトブキ飛行隊 (2019-2019) Discography / Music Collection [4 CDs] [MP3]'
#   },
#   'links': [{
#       'rel': 'alternate',
#       'type': 'text/html',
#       'href': 'https://nyaa.si/download/1152087.torrent'
#   }],
#   'link': 'https://nyaa.si/download/1152087.torrent',
#   'id': 'https://nyaa.si/view/1152087',
#   'guidislink': False,
#   'published': 'Mon, 17 Jun 2019 18:30:28 -0000',
#   'published_parsed': time.struct_time(tm_year=2019, tm_mon=6, tm_mday=17, tm_hour=18, tm_min=30, tm_sec=28, tm_wday=0, tm_yday=168, tm_isdst=0),
#   'nyaa_seeders': '0',
#   'nyaa_leechers': '0',
#   'nyaa_downloads': '0',
#   'nyaa_infohash': '0a9500d3c36bfd19121dffc75ef7c125d523cffd',
#   'nyaa_categoryid': '2_2',
#   'nyaa_category': 'Audio - Lossy',
#   'nyaa_size': '368.6 MiB',
#   'nyaa_comments': '0',
#   'summary': '<a href="https://nyaa.si/view/1152087">#1152087 | [Nemuri] Kōya no Kotobuki Hikōtai 荒野のコトブキ飛行隊 (2019-2019) Discography / Music Collection [4 CDs] [MP3]</a> | 368.6 MiB | Audio - Lossy | 0A9500D3C36BFD19121DFFC75EF7C125D523CFFD',
#   'summary_detail': {
#       'type': 'text/html',
#       'language': None,
#       'base': 'https://nyaa.si/?page=rss&',
#       'value': '<a href="https://nyaa.si/view/1152087">#1152087 | [Nemuri] Kōya no Kotobuki Hikōtai 荒野のコトブキ飛行隊 (2019-2019) Discography / Music Collection [4 CDs] [MP3]</a> | 368.6 MiB | Audio - Lossy | 0A9500D3C36BFD19121DFFC75EF7C125D523CFFD'
#   }
# }

class Scraper():
    def __init__(self):
        self.base = 'https://nyaa.si/?page=rss&'
        self.params = {
            'f': 0,
            'c': '0_0',
            'q': '',
            'p': 1,
            's': 'id',
            'o': 'desc',
        }
        self.feed = None

    def filter(self, filter):
        self.params['f'] = filter

    def category(self, category):
        self.params['c'] = category

    def query(self, query):
        self.params['q'] = query

    def page(self, page):
        self.params['p'] = page

    def sort(self, sort):
        self.params['s'] = sort

    def order(self, order):
        self.params['o'] = order

    def search(self):
        params = urllib.parse.urlencode(self.params)
        self.feed = feedparser.parse(self.base + params)
        for entry in self.feed.entries:
            print()
            print(entry.title)
            print(entry.nyaa_size)
            print(entry.nyaa_seeders, 'seeders')
