import math
import os

import config


def file(length, path, offset):
    path = './complete/' + path
    dirname = os.path.dirname(path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    return {
        'length': length,
        'path': path,
        'offset': offset,
        'stream': open(path, 'wb'),
        'complete': False,
        'started': False,
    }


def block():
    return {
        'length': config.BLOCK_SIZE,
        'value': b'',
        'requesting': None,
    }


def piece(value=b''):
    num_blocks = math.ceil(config.PIECE_SIZE / config.BLOCK_SIZE)
    return {
        'value': value,
        'blocks': [block() for _ in range(num_blocks)],
        'peers': set(),
        'complete': False,
    }
