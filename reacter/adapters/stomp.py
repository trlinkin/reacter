#------------------------------------------------------------------------------#
# StompAdapter
#
import os
import socket
import yaml
from reacter.util import Util
from reacter.config import Config
import reacter.adapter as adapter
from reacter.agent import Message

class StompAdapter(adapter.Adapter):
  DEFAULT_QUEUE='/queue/monitoring/metrics'

  def __init__(self, name):
    super(StompAdapter,self).__init__(name)

  def connect(self, **kwargs):
    self.host = kwargs.get('host') or Util.DEFAULT_HOSTNAME
    self.port = int(kwargs.get('port')) or Util.DEFAULT_PORT
    self.queue = kwargs.get('queue') or DEFAULT_QUEUE
    self.retry = bool(kwargs.get('retry')) or True

    try:
      self._connection = stompy.simple.Client(
        host=self.host,
        port=self.port
      )

      self._connection.connect(
        username=self.username,
        password=self.password,
        clientid='%s-%s-%s' % ('reacter', socket.gethostname(), os.getpid())
      );

    # we're connected, say so
      return True

    except stompy.stomp.ConnectionError as e:
      raise adapter.AdapterConnectionFailed(e)

  def send(self, message):
    return False

  def poll(self):
    self._connection.subscribe(queue, ack='auto')

    try:
      frame = self._connection.get(block=True)
      return Message(yaml.safe_load(frame.body))

    except stompy.frame.UnknownBrokerResponseError as e:
      raise adapter.AdapterConnectionFailed(e)