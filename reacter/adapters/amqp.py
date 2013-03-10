#------------------------------------------------------------------------------#
# AmqpAdapter
#
import os
import json
import pika
from reacter.util import Util
from reacter.config import Config
import reacter.adapter as adapter
from reacter.agent import Message

AMQP_DEFAULT_QUEUE_NAME='reacter'
AMQP_DEFAULT_EXCHANGE='amq.fanout'
AMQP_DEFAULT_VHOST='/'
AMQP_DEFAULT_POLLSIZE=1

class AmqpAdapter(adapter.Adapter):

  def __init__(self, name):
    super(AmqpAdapter,self).__init__(name)

  def connect(self, **kwargs):
    credentials = None

  # set credentials if they were specified
    if self.config.get('username') and self.config.get('password'):
      credentials = pika.PlainCredentials(self.config.get('username'), self.config.get('password'))

  # define some other things that we'll need
    self._queue = (self.config.get('queue') or AMQP_DEFAULT_QUEUE_NAME)
    self._exchange = (self.config.get('exchange') or AMQP_DEFAULT_EXCHANGE)
    self._vhost = (self.config.get('vhost') or AMQP_DEFAULT_VHOST)

  # set connection parameters
    parameters = pika.ConnectionParameters(self.config.get('hostname'), self.config.get('port'), self._vhost, credentials)


  # connect
    Util.info('amqp: Connecting to', self.config.get('hostname'))
    self._connection = pika.BlockingConnection(parameters)
    self._channel = self._connection.channel()

  # create queue
    Util.debug("amqp: Creating queue '%s' with options: %s %s %s %s" % (
      self._queue,
      ('TTL' if self.config.get('ttl')        else ''),
      ('DUR' if self.config.get('durable')    else ''),
      ('XCL' if self.config.get('exclusive')  else ''),
      ('AD'  if self.config.get('autodelete') else '')
    ))

    self._channel.queue_declare(queue=self._queue,
      durable=(self.config.get('durable') or False),
      exclusive=(self.config.get('exclusive') or True),
      auto_delete=(self.config.get('autodelete') or True),
      arguments={
        'x-message-ttl': self.config.get('ttl')
      })

  # bind queue
    Util.debug('amqp: Binding %s -> %s' % (self._queue, self._exchange))
    self._channel.queue_bind(queue=self._queue, exchange=self._exchange)


  def send(self, message):
    pass

  def poll(self):
    messages = []
    acktag = None
    rv = []

    for frame, properties, body in self._channel.consume(self._queue):
    # add message
      messages.append(body)

      if len(messages) > (self.config.get('pollsize') or AMQP_DEFAULT_POLLSIZE):
        acktag = frame.delivery_tag
        break


    for message in Message.parse(messages):
      rv.append(message)

  # acknowledge up to and including <acktag>
    if acktag:
      self._channel.basic_ack(acktag, True)

    return rv


  def disconnect(self):
    try:
      self._channel.cancel()
    except Exception, e:
      pass

  # bubble up
    super(AmqpAdapter,self).disconnect()