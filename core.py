#------------------------------------------------------------------------------#
# Core
#
import os
import sys
import time
import imp
from socket import gethostname
import stompy
from util import Util
from agent import Agent, Message

class Core:
  DEFAULT_QUEUE='/queue/monitoring/metrics'

  def __init__(self):
    self.agents = {}
    self.handlers = {}
    self.wait_reconnect = (1,1)

  def add_agent(self, agent):
    path = sys.path
    path.insert(1, '/etc/reacter/agents')
    path.insert(1, os.path.expanduser('~/.reacter/agents'))
    path.insert(1, './agents')

    try:
      (_file, _path, _description) = imp.find_module(agent, path)
      agent_module = imp.load_module(agent, _file, _path, _description)
      agent_class = getattr(agent_module, Util.camelize(agent, suffix='Agent'))
      self.agents[agent] = agent_class(agent)
    finally:
      _file.close()


  def connect(self, host=Util.DEFAULT_HOSTNAME, port=Util.DEFAULT_PORT, username=None, password=None, queue=DEFAULT_QUEUE):
    self.queue_name = queue
    self.host = host
    self.port = int(port)
    self.username = username
    self.password = password # iffy

    self.start_connection()

    return True

  def start_connection(self):
    while True:
      try:
        self.conn = stompy.simple.Client(
          host=self.host,
          port=self.port
        )

        self.conn.connect(
          username=self.username,
          password=self.password,
          clientid='%s-%s-%s' % ('reacter', gethostname(), os.getpid())
        );

        print "Connected to %s:%s" % (self.host, self.queue_name)

      # we're connected, break the connect-retry loop
        break

      except stompy.stomp.ConnectionError as e:
        self.wait_connect()
        continue

  def send(self, message, headers=None):
    self.conn.put(message,
      destination=self.queue_name,
      conf=headers)

  def process(self, queue):
    self.conn.subscribe(queue, ack='auto')
    self.running = True

    while self.running:
      try:
        frame = self.conn.get(block=True)
        self.dispatch_message(Message(frame))
        self.wait_reconnect = (1,1)

      except stompy.frame.UnknownBrokerResponseError as e:
        self.wait_connect()
        self.start_connection()
        continue

  def wait_connect(self):
  # wait along the fibonacci sequence to reconnect...
    print 'Could not connect to message queue, retrying in %ds...' % self.wait_reconnect[1]
    time.sleep(self.wait_reconnect[0]+self.wait_reconnect[1])

  # max retry wait time
    if self.wait_reconnect[1] < 55:
      self.wait_reconnect = (self.wait_reconnect[1], self.wait_reconnect[0]+self.wait_reconnect[1])

  def dispatch_message(self, message):
    for name, agent in self.agents.items():
      agent.received(message)