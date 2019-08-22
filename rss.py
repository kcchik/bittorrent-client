import sys
import curses
import curses.textpad
import requests

import feedparser


def main(stdscr):
    if len(sys.argv) != 2:
        print('Error')
        sys.exit(1)

    feed = feedparser.parse('https://nyaa.si/?page=rss&c=1_2&q={}'.format(sys.argv[1]))

    curses.use_default_colors()
    curses.curs_set(0)
    height, width = stdscr.getmaxyx()
    resultpad = curses.newpad(300, width)

    k = 0
    index = 0
    scroll = 0
    while True:
        stdscr.addstr(0, 0, 'Koji BitTorrent Client', curses.A_BOLD)
        stdscr.refresh()

        if k == curses.KEY_DOWN and index < len(feed['entries']) - 1:
            index += 1
            if index > scroll + height / 3 - 2:
                scroll += 1
        elif k == curses.KEY_UP and index > 0:
            index -= 1
            if index < scroll:
                scroll -= 1
        elif k == 10:
            res = requests.get(feed['entries'][index]['link'])
            with open('tmp/tmp.torrent', 'wb') as file:
                file.write(res.content)
            sys.exit(0)

        for i, entry in enumerate(feed['entries']):
            if i == index:
                resultpad.addstr(3 * i, 0, ' {} '.format(entry['title']), curses.A_BOLD | curses.A_STANDOUT)
            else:
                resultpad.addstr(3 * i, 0, ' {} '.format(entry['title']), curses.A_BOLD)
            resultpad.addstr(3 * i + 1, 0, ' {} - {} seeders'.format(entry['nyaa_size'], entry['nyaa_seeders']))

        resultpad.refresh(scroll * 3, 0, 2, 0, height - 1, width - 1)
        k = stdscr.getch()


if __name__ == '__main__':
    curses.wrapper(main)

# 'link': 'https://nyaa.si/download/1169465.torrent',
# 'id': 'https://nyaa.si/view/1169465',
# 'nyaa_seeders': '723',
# 'nyaa_leechers': '310',
# 'nyaa_downloads': '2211',
# 'nyaa_infohash': '63890e867b87f9a6df8b7369ea5303c0a8f8e9ba',
# 'nyaa_category': 'Anime - Raw',
# 'nyaa_size': '380.9 MiB',
