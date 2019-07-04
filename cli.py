import sys
import threading
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
            {
                'id': 2,
                'name': ['--method'],
                'args': ['1', '2'], 'description': 'Select piece requesting method'
            },
        ]
        self.commands = [
            {
                'id': 0,
                'name': 'torrent',
                'description': 'Torrent using .torrent file'
            },
            {
                'id': 1,
                'name': 'magnet',
                'description': 'Torrent using magnet link'
            },
        ]


    def parse(self):
        value = ''
        args = iter(self.args)
        for arg in args:
            if arg[0] == '-':
                self.parse_option(arg)
            else:
                self.parse_command(arg)
                value = next(args, '')
        if not config.COMMAND:
            self.help()
        if not value:
            print('No arguments given for command: {}'.format(config.COMMAND))
            sys.exit()
        return value


    def parse_option(self, arg):
        args = arg.split('=', 1)
        option = next((opt for opt in self.options if args[0] in opt['name']), None)
        if not option:
            self.help(message='Unknown option: {}'.format(args[0]))
        elif option['id'] == 0:
            self.help()
        elif option['id'] == 1:
            config.VERBOSE = True
        elif option['id'] == 2:
            if len(args) > 1 and args[1] in option['args']:
                config.METHOD = args[1]
            else:
                print('Invalid argument for option: {}'.format(option['name'][0]))
                sys.exit()


    def parse_command(self, arg):
        command = next((cmd['id'] for cmd in self.commands if arg == cmd['name']), -1)
        if command == 0:
            config.COMMAND = 'torrent'
        elif command == 1:
            config.COMMAND = 'magnet'
        else:
            self.help(message='Unknown command: {}'.format(arg))


    def help(self, message=None):
        if message:
            print(message)
        print('Usage: {} <command> <arg>'.format(self.name))
        print()
        print('Commands:')
        for command in self.commands:
            print('    {}'.format(command['name']).ljust(20), command['description'])
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

def connected():
    if not config.VERBOSE:
        print('\rConnected!   ')

def loading(iteration, total, extra=''):
    if not config.VERBOSE:
        filled = int(100 * iteration // total)
        progress_bar = '\033[94m•\033[0m' * filled + '◦' * (100 - filled)
        print('\r{} {}/{} {}'.format(progress_bar, iteration, total, extra), end='\b')
        if iteration == total:
            print()
            print('\033[92m✔\033[0m Complete in {:.3f}s!'.format(time.time() - config.START_TIME))


def printf(message, prefix=''):
    if config.VERBOSE:
        print(prefix.ljust(20), message)
