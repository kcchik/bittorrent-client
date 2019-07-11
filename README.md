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
* [ ] Reconnect peers
* [ ] Pause/resume torrents

### Notes
Use events instead of checking every 0.1s. This prevents Koji from requesting the same piece twice during the metadata stage.
