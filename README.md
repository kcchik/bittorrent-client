# Koji

BitTorrent Client for [nyaa.si](https://nyaa.si/)

### Requirements

* Python
* Pipenv

### Installation

Clone this repo
```sh
git clone https://github.com/kcchik/koji.git

cd koji
```

Start pipenv shell and install dependencies
```sh
# must run/develop in pipenv
pipenv shell

pipenv install
```

To exit pipenv, use `exit`

### Start

```sh
python koji -h
```

### TODO

* [x] Torrents with multiple files
* [x] Manage inactive peers (wait for piece to become available)
* [x] Magnet links
* [ ] Piece management
* [ ] Incomplete torrents
* [ ] Send pieces
