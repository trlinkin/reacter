#------------------------------------------------------------------------------#
# Core
#
import os
import sys
import time
import imp
import stompy
from socket import gethostname
from config import Config
from util import Util
from agent import Agent, Message

class Core:
  DEFAULT_QUEUE='/queue/monitoring/metrics'

  def __init__(self):
    self.running = False
    self.agents = {}
    self.handlers = {}
    self.wait_reconnect = (1,1)


  def connect(self, host=Util.DEFAULT_HOSTNAME, port=Util.DEFAULT_PORT, username=None, password=None, queue=DEFAULT_QUEUE, retry=True):
    self.queue_name = queue
    self.host = host
    self.port = int(port)
    self.username = username
    self.password = password # iffy
    self.auto_retry = retry

    return self.start_connection()


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

      # clear disconnect, emit connected message
        if self.running:
          self.dispatch_message(Util.get_event_message('disconnected'))

        self.dispatch_message(Util.get_event_message('connected'))

        Util.info("Connected to", self.host, self.queue_name)

      # we're connected, break the connect-retry loop
        return True

      except stompy.stomp.ConnectionError as e:
        if self.auto_retry:
          self.wait_connect()
          continue
        else:
          Util.error("Connection to %s:%s failed" % (self.host, self.port))
          return False


  def send(self, message, headers=None):
    self.conn.put(message,
      destination=self.queue_name,
      conf=headers)


  def add_agent(self, agent):
    path = sys.path
    agents_custom_path = Config.get('agents.options.path')

    path.insert(0, '/etc/reacter/agents')
    path.insert(0, os.path.expanduser('~/.reacter/agents'))
    path.insert(0, './agents')

  # add custom agent paths as most specific search path(s)
    if agents_custom_path:
      if isinstance(agents_custom_path, list):
        for a in agents_custom_path:
          path.insert(0, os.path.expanduser(a))
      else:
        path.insert(0, os.path.expanduser(agents_custom_path))

  # attempt agent load
    _file = None
    _path = None
    _description = None

    try:
      (_file, _path, _description) = imp.find_module(agent, path)
      agent_module = imp.load_module(agent, _file, _path, _description)
      agent_class = getattr(agent_module, Util.camelize(agent, suffix='Agent'))
      self.agents[agent] = agent_class(agent)
    finally:
      if _file:
        _file.close()


  def process(self, queue):
    self.conn.subscribe(queue, ack='auto')
    self.running = True

    while self.running:
      try:
        frame = self.conn.get(block=True)
        self.dispatch_message(Message(frame))
        self.wait_reconnect = (1,1)

      except stompy.frame.UnknownBrokerResponseError as e:
      # emit disconnected message
        self.dispatch_message(Util.get_event_message('disconnected', 'error'))

        self.wait_connect()
        self.start_connection()
        continue


  def wait_connect(self):
  # wait along the fibonacci sequence to reconnect...
    Util.error('Could not connect to message queue, retrying in %ds...' % self.wait_reconnect[1])
    time.sleep(self.wait_reconnect[0]+self.wait_reconnect[1])

  # max retry wait time
    if self.wait_reconnect[1] < 55:
      self.wait_reconnect = (self.wait_reconnect[1], self.wait_reconnect[0]+self.wait_reconnect[1])


  def dispatch_message(self, message):
    last_return_value = None

  # iterate through all agents, dispatching the message to each of them
  #   if agents.options.chain == true, then process the agents sequentially,
  #   passing the output of one agent into the next one in the chain. if the
  #   last agent did not return anything, pass in the original message
  #
  #   else, process them in parallel, passing the original message to all
  #   agents simultaneously
  #
  #TODO: actually implemet the "parallel"; use gevent to do this async
  #
    for name, agent in self.agents.items():
      if Config.get('agents.options.chain'):
        last_return_value = agent.received(last_return_value or message)
      else:
        agent.received(message)