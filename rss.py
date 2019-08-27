import curses
import curses.textpad
import requests

import feedparser


def main(stdscr):
    curses.use_default_colors()
    stdscr.addstr(0, 0, 'Koji BitTorrent Client', curses.A_BOLD)
    stdscr.refresh()

    index = 0
    option = 0
    key = 0
    item_height = 3
    state = 0
    scroll_state = 0
    height, width = stdscr.getmaxyx()
    item_pad = curses.newpad(75 * item_height, width)

    while key != ord('q'):
        stdscr.refresh()
        if key == ord(':'):
            key = 0
            state = 0
            continue

        if state == 0:
            curses.curs_set(1)
            stdscr.addstr(1, 0, ':')
            search_win = curses.newwin(1, width - 1, 1, 1)
            stdscr.refresh()
            search_pad = curses.textpad.Textbox(search_win)

            try:
                search = search_pad.edit()
            except KeyboardInterrupt:
                break

            curses.curs_set(0)
            item_pad.clear()
            item_pad.refresh(0, 0, 2, 0, height - 1, width - 1)
            stdscr.addstr(3, 0, 'Scraping nyaa.si for torrents...')
            stdscr.refresh()

            feed = feedparser.parse('https://nyaa.si/?page=rss&q={}'.format(search))
            if not feed['entries']:
                stdscr.addstr(3, 0, 'No results'.ljust(width - 1))
                stdscr.refresh()
                continue

            state = 1
            continue

        elif state == 1:
            if key == curses.KEY_DOWN and index < len(feed['entries']) - 1:
                index += 1
                if index > scroll_state + height / item_height - item_height + 1:
                    scroll_state += 1
            elif key == curses.KEY_UP and index > 0:
                index -= 1
                if index < scroll_state:
                    scroll_state -= 1
            elif key == curses.KEY_RIGHT or key == 10:
                key = 0
                state = 2
                continue

            for i, entry in enumerate(feed['entries']):
                bold = curses.A_BOLD
                dim = curses.A_DIM
                if i == index:
                    bold |= curses.A_STANDOUT
                    dim |= curses.A_STANDOUT
                item_pad.addstr(item_height * i + 1, 0, entry['title'].ljust(width - 1), bold)
                plural = 's' if entry['nyaa_seeders'] != '1' else ''
                item_pad.addstr(item_height * i + 2, 0, '{} - {} seeder{}'.format(entry['nyaa_size'], entry['nyaa_seeders'], plural).ljust(width - 1), dim)
            item_pad.refresh(scroll_state * item_height, 0, 2, 0, height - 1, width - 1)

        elif state == 2:
            if key == curses.KEY_UP:
                option = 0
            elif key == curses.KEY_DOWN:
                option = 1
            elif key == curses.KEY_LEFT:
                key = 0
                state = 1
                continue
            elif key == 10:
                res = requests.get(feed['entries'][index]['link'])
                with open('tmp/tmp.torrent', 'wb') as file:
                    file.write(res.content)
                break

            stdscr.addstr((index - scroll_state) * item_height + item_height, 0, '   Stream'.ljust(width), curses.A_BOLD | curses.A_STANDOUT)
            stdscr.addstr((index - scroll_state) * item_height + item_height + 1, 0, '   Download'.ljust(width), curses.A_BOLD | curses.A_STANDOUT)
            stdscr.addstr((index - scroll_state) * item_height + item_height + option, 0, ' >', curses.A_BOLD | curses.A_STANDOUT)

        try:
            key = stdscr.getch()
        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    curses.wrapper(main)
