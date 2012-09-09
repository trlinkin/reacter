#------------------------------------------------------------------------------#
# ZeromqAdapter
#
import os
import yaml
import zmq
from reacter.util import Util
from reacter.config import Config
import reacter.adapter as adapter
from reacter.agent import Message

class ZeromqAdapter(adapter.Adapter):
  DEFAULT_TRANSPORT='ipc:///tmp/reacter.zmq'

  def __init__(self, name):
    super(ZeromqAdapter,self).__init__(name)
    self._context = zmq.Context()

  def connect(self, **kwargs):
    self._sender = self.config.get('sender')

    if self._sender:
      self._queue = self._context.socket(zmq.PUSH)
    else:
      self._queue = self._context.socket(zmq.PULL)

    transport = self.config.get('transport')

    if transport:
      if '://' in transport:
        self.transport = transport
      else:
        if transport == 'tcp':
          if self.config.get('host') and self.config.get('port'):
            self.transport = '%s://%s:%d' % (transport, self.config.get('host'), int(self.config.get('port')))
        elif transport == 'ipc':
          if self.config.get('socket'):
            self.transport = '%s://%s' % self.config.get('socket')
    else:
      self.transport = self.DEFAULT_TRANSPORT

  # connect to the transport
    if self._sender:
      self._queue.bind(self.transport)
    else:
      self._queue.connect(self.transport)

  def send(self, message):
    self._queue.send('---\n' + yaml.dump(message.data))

  def poll(self):
    #try:

    message = self._queue.recv()
    return Message(yaml.safe_load(message))

    #except Exception as e:
      #raise adapter.AdapterConnectionFaulted(e)