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
    # senders use PUSH socket
      self._queue = self._context.socket(zmq.PUSH)
    else:
    # receivers use PULL socket
      self._queue = self._context.socket(zmq.PULL)

    transport = self.config.get('transport')

    if transport:
    # whole transport string is specified in the config, take its word for it
      if '://' in transport:
        self.transport = transport
      else:
    # otherwise, build the string from parameters
    #   TCP
        if transport == 'tcp':
        # requires: host, port
          if self.config.get('host') and self.config.get('port'):
            self.transport = '%s://%s:%d' % (transport, self.config.get('host'), int(self.config.get('port')))

    #   IPC
        elif transport == 'ipc':
        # requires: socket (path)
          if self.config.get('socket'):
            self.transport = '%s://%s' % self.config.get('socket')
    else:
    # fallback to default local socket at /tmp/reacter.zmq
      self.transport = self.DEFAULT_TRANSPORT

  # connect to the transport
    if self._sender:
    # senders bind
      Util.info('zeromq: Binding to %s' % self.transport)
      self._queue.bind(self.transport)

    else:
    # receivers connect
      Util.info('zeromq: Connecting to %s' % self.transport)
      self._queue.connect(self.transport)


  def send(self, message):
    self._queue.send('---\n' + yaml.dump(message.data))


  def poll(self):
    message = self._queue.recv()
    return Message(yaml.safe_load(message))


  def disconnect(self):
    self._context.destroy()

  # bubble up
    super(ZeromqAdapter,self).disconnect()