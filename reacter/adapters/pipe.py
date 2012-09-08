#------------------------------------------------------------------------------#
# PipeAdapter
#
import os
import yaml
from reacter.util import Util
from reacter.config import Config
import reacter.adapter as adapter
from reacter.agent import Message

class PipeAdapter(adapter.Adapter):
  DEFAULT_FILENAME='/tmp/reacter.queue'

  def __init__(self, name):
    super(PipeAdapter,self).__init__(name)

  def connect(self, **kwargs):
    self.filename = kwargs.get('filename') or self.DEFAULT_FILENAME

    try:
      os.mkfifo(self.filename)
      return True

    except OSError as e:
      #raise adapter.AdapterConnectionFailed(e)
      pass

  def send(self, message):
    try:
      fifo = open(self.filename, 'w')
      print >> fifo, yaml.dump(message.data)      
    except:
      pass


  def poll(self):
    try:
      fifo = open(self.filename, 'r')
      rv = []

    # load all documents from the fifo
      for message in yaml.safe_load_all(fifo.read()):
        rv.append(Message(message))

      return rv

    except Exception as e:
      raise adapter.AdapterConnectionFaulted(e)