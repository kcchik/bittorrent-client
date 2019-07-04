import sys
import hashlib
import struct
import time

import config
import factory
import cli


def disconnect(self):
    if self.piece_index != -1:
        if config.METHOD == 1:
            config.manager.pieces[self.piece_index]['requesting'] = False
        else:
            config.manager.pieces[config.manager.progress]['blocks'][self.piece_index]['requesting'] -= 1
    self.socket.close()
    self.state['connected'] = False
    sys.exit()

def handle_block_2(self, payload):
    i, offset = struct.unpack('>II', payload[:8])
    block = payload[8:]
    if config.manager.progress != i:
        return
    piece = config.manager.pieces[i]
    piece['blocks'][offset // config.BLOCK_SIZE]['value'] = block
    self.piece_index = -1
    if sum(1 for block in piece['blocks'] if not block['value']) == 0:
        if hashlib.sha1(b''.join([block['value'] for block in piece['blocks']])).digest() == piece['value']:
            cli.printf('\033[92m✓\033[0m {}/{}'.format(i + 1, len(config.manager.pieces)), prefix=self.address[0])
            piece['complete'] = True
        else:
            cli.printf('\033[91m✗\033[0m {}/{}'.format(i + 1, len(config.manager.pieces)), prefix=self.address[0])
            piece['blocks'] = [factory.block() for _ in piece['blocks']]
            self.has.remove(i)

def send_request_2(self):
    progress = config.manager.progress
    piece = config.manager.pieces[progress]
    while self.piece_index == -1:
        progress = config.manager.progress
        if progress in self.has:
            piece = config.manager.pieces[progress]
            for i, block in enumerate(piece['blocks']):
                if block['requesting'] < 1 and not block['value']:
                    block['requesting'] += 1
                    self.piece_index = i
                    cli.printf('\033[92mb\033[0m {}/{}'.format(i + 1, len(piece['blocks'])), prefix=self.address[0])
                    break
        if self.piece_index != -1:
            time.sleep(0.1)
        if not any(not file['complete'] for file in config.manager.files):
            self.disconnect()
    message = struct.pack(
        '>IBIII',
        13,
        6,
        progress,
        self.piece_index * config.BLOCK_SIZE,
        piece['blocks'][self.piece_index]['length']
    )
    self.send(message)