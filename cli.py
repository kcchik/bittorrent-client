import sys
import time

import config


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
