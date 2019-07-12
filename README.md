# Koji
Command line BitTorrent client for [nyaa.si](https://nyaa.si/)

### Requirements
* Python
* Pipenv

### Installing
Open virtualenv
```sh
pipenv shell
```

Install dependencies and start
```sh
pipenv install

python koji
```

### To Do
* [x] Multi-file torrents
* [x] Magnet links
* [ ] Queues
* [ ] Reconnect peers
* [ ] Pause/resume torrents

### Notes
Use events instead of checking every 0.1s. This prevents Koji from requesting the same piece twice during the metadata stage.

#### Metadata
1. Connect
2. Send handshake
3. Receive handshake
4. Receive metadata handshake
5. Receive bitfield and haves
6. Send metadata request
7. Receive metadata piece
8. Repeat 6 and 7

#### Pieces
1. Connect
2. Send handshake
3. Receive handshake
4. Receive bitfields and haves
5. Send interested
6. Receive unchoke
7. Send request
8. Receive block
9. Repeat 7 and 8
