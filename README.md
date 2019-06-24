# Koji

BitTorrent Client for [nyaa.si](https://nyaa.si/)

### Requirements

* Python
* Pipenv

### Installation

Clone this repo
```shell
git clone https://github.com/kcchik/koji.git

cd koji
```

Start shell and install dependencies
```shell
# must run/develop in pipenv
pipenv shell

pipenv install
```

To exit pipenv, use `exit`

### Usage

```sh
koji [options] <command> [<args>]
```

#### Commands

**torrent:** Torrent using .torrent file

**magnet:**  Torrent using magnet link

### TODO

* [x] Torrents with multiple files
* [x] Manage inactive peers (wait for piece to become available)
* [x] Magnet links
* [ ] Incomplete torrents
* [ ] Multiple requests
* [ ] Send pieces
