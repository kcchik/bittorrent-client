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
* [ ] Reconnect peers
* [ ] Pause/resume torrents

### Piece management

#### Method 1
Pieces requested simultaneously. Blocks requested one after another.

Slow pieces will create conjestion, writing happens in large chunks

#### Method 2
Pieces requested one after another. Blocks requested simultaneously.

Pieces finish in order, but peers won't request from the next piece until the current one is complete
