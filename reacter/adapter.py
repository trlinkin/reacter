#------------------------------------------------------------------------------#
# Adapter
#
from config import Config

class AdapterConnectionFailed(Exception):
  pass

class AdapterConnectionFaulted(Exception):
  pass

class Adapter(object):
  def __init__(self, name):
    self.name = name

  # agent's config is scoped to reacter.adapter.<adapter_name>.*
    self.config = Config.get('adapter', {})

# implement: connect to the data source
  def connect(self, **kwargs):
    return False

# implement: send a message suitable for consumption by an instance of reacter
#            in listen mode
  def send(self, message):
    return False

# implement: poll for a new message and return it
  def poll(self):
    return False