import sys

import config

class Cli():
    def __init__(self, args):
        self.args = args
        self.options = {
            '-h': 0, '--help': 0,
        }
        self.commands = {
            'torrent': 0,
            'magnet': 1,
        }

    def parse(self):
        if len(self.args) < 2:
            self.help()
        while len(self.args) > 1 and self.args[1][0] == '-':
            option = self.args.pop(1)
            if option in self.options:
                type = self.options[option]
                if type == 0:
                    self.help()
            else:
                self.help(message='Unknown option: {}'.format(option))

        if self.args[1] in self.commands:
            if len(self.args) <= 2:
                print('No arguments given for command: {}'.format(self.args[1]))
                sys.exit()
            if self.commands[self.args[1]] == 1:
                config.is_magnet = True
            return self.args[2]
        else:
            self.help(message='Unknown command: {}'.format(self.args[1]))

    def help(self, message=None):
        if message:
            print(message)
        print('Usage: {} [options] <command> [<args>]'.format(self.args[0]))
        print()
        print('Commands:')
        print('    torrent'.ljust(20), 'Torrent using .torrent file')
        print('    magnet'.ljust(20), 'Torrent using magnet link')
        print()
        print('Options:')
        print('    -h, --help'.ljust(20), 'Show this help message and exit')
        print()
        sys.exit()
