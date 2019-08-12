import sys
import time

import config


class Parser():
    def __init__(self, args):
        self.name = args.pop(0)
        self.args = args
        self.options = [
            {
                'id': 0,
                'name': ['-h', '--help'],
                'description': 'Show this help message and exit'
            },
            {
                'id': 1,
                'name': ['-v', '--verbose'],
                'description': 'Run in verbose output mode'
            },
        ]


    def parse(self):
        value = ''
        for arg in self.args:
            if arg[0] == '-':
                self.option(arg)
            elif value:
                self.help(message='Specify a single .torrent file')
            else:
                value = arg
        if not value:
            self.help()
        return value


    def option(self, arg):
        args = arg.split('=', 1)
        option = next((opt for opt in self.options if args[0] in opt['name']), None)
        if not option:
            self.help(message='Unknown option: {}'.format(args[0]))
        elif option['id'] == 0:
            self.help()
        elif option['id'] == 1:
            config.VERBOSE = True


    def help(self, message=None):
        if message:
            print(message)
        print('Usage: {} <torrent>'.format(self.name))
        print()
        print('Options:')
        for option in self.options:
            name = ', '.join(option['name'])
            if 'args' in option:
                name += '=<{}>'.format('|'.join(option['args']))
            print('    {}'.format(name).ljust(20), option['description'])
        print()
        sys.exit()


def connecting():
    if not config.VERBOSE:
        print('\rConnecting...', end='\b')


def connected(total):
    if not config.VERBOSE:
        print('\rConnected!   ')
        loading(0, total)


def loading(iteration, total):
    if not config.VERBOSE:
        filled = int(100 * iteration // total)
        progress_bar = '\033[94m•\033[0m' * filled + '◦' * (100 - filled)
        print('\r{} {}/{}'.format(progress_bar, iteration, total), end='\b')
        if iteration == total:
            print()
            print('\033[92m✔\033[0m Complete in {:.3f}s!'.format(time.time() - config.START_TIME))
            print()


def printf(message, prefix=''):
    if config.VERBOSE:
        print(prefix.ljust(20), message)
