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
* [ ] Reconnect peers
* [ ] Pause/resume torrents

### Notes
Start a thread for tracker to update peers
Catch all possible errors and log all disconnects

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
