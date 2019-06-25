import sys
import threading
import time

import config

class Cli():
    def __init__(self, args):
        self.args = args
        self.options = {
            '-h': 0, '--help': 0,
            '-v': 1, '--verbose': 1,
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
                elif type == 1:
                    config.verbose = True
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
        print('    -v, --verbose'.ljust(20), 'Run in verbose output mode')
        print()
        sys.exit()

class spinner(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.event = threading.Event()

    def run(self):
        while not self.event.is_set():
            for spin in '⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏':
                print('\r{} Connecting'.format(spin), end='\b')
                self.event.wait(0.1)

def loading(iteration, total):
    filled = int(100 * iteration // total)
    bar = '\033[94m•\033[0m' * filled + '◦' * (100 - filled)
    print('\r{} {}/{}'.format(bar, iteration, total), end='\b')
    if iteration == total:
        print()
        print('\033[92m✔\033[0m Complete!')

def printf(message, prefix=''):
    if config.verbose:
        print(prefix.ljust(20), message)
