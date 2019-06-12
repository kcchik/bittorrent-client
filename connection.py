from threading import Thread

class Connection(Thread):
  def __init__(self, peer):
    Thread.__init__(self)
