# Koji

Command line BitTorrent client for [nyaa.si](https://nyaa.si/)

### Requirements

* Python
* Pipenv

### Developing

Clone this repo
```sh
git clone https://github.com/kcchik/koji.git

cd koji
```

Launch Pipenv shell and install dependencies
```sh
# always develop in pipenv
pipenv shell

pipenv install
```

Start script
```sh
python koji -h
```

### TODO

* [x] Multi-file torrents
* [x] Magnet links
* [ ] Pause/resume torrents

### Working

* [x] Single file torrent
* [x] Multi file torrent
* [ ] Single file magnet
* [x] Multi file magnet

### Piece management

#### Method 1
Pieces requested simultaneously. Blocks requested one after another.
```sh
# 3 peers, 3 pieces, 3 blocks/piece

peer_a: (0, 0) -> (0, 1) -> (0, 2)

peer_b: (1, 0) -> (1, 1) -> (1, 2)

peer_c: (2, 0) -> (2, 1) -> (2, 2)
```
Slow pieces will create conjestion, writing happens in large chunks

#### Method 2
Pieces requested one after another. Blocks requested simultaneously.
```sh
# 3 peers, 3 pieces, 3 blocks/piece

peer_a: (0, 0) -> (1, 0) -> (2, 0)

peer_b: (0, 1) -> (1, 1) -> (2, 1)

peer_c: (0, 2) -> (1, 2) -> (2, 2)
```
Pieces finish in order, but peers won't request from the next piece until the current one is complete
