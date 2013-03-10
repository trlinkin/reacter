#------------------------------------------------------------------------------#
# Core
#
import os
import sys
import time
import imp
import json
import copy
from string import capwords
from socket import gethostname
from config import Config
from util import Util
from agent import Agent, Message
import adapter

class Core:
  def __init__(self):
    self.listening = False
    self.agents = []
    self.adapters = []
    self.handlers = {}
    self.wait_reconnect = (1,1)

  def connect(self, **kwargs):
    self.auto_retry = bool(kwargs.get('retry')) or True

  # set runtime options for the current adapter
    if self.adapter:
      self.adapter.config['sender'] = bool(kwargs.get('sender'))
      return self.start_connection()

    return False

  def start_connection(self):
    while True:
      try:
        self.adapter.connect()

      # clear disconnect, emit connected message
        if self.listening:
          self.dispatch_message(Util.get_event_message('disconnected'))

        self.dispatch_message(Util.get_event_message('connected'))

        Util.info('Connected to', self.adapter.name, 'adapter')

      # we're connected, break the connect-retry loop
        return True

      except adapter.AdapterConnectionFailed as e:
        if self.auto_retry:
          self.wait_connect()
          continue
        else:
          Util.error('Connection to', self.adapter.name, 'adapter failed')
          return False


  def disconnect(self):
    self.adapter.disconnect()


  def send(self, body):
  # send all messages
    for message in Message.parse(body):
      self.adapter.send(message)

# set adapter
  def set_adapter(self, name):
    Util.debug('Setting adapter:', name)

    self.adapter = self.load_plugin(
      plugin_type='adapter',
      name=name,
      config_root='adapter'
    )

    return self.adapter

# load an agent by name
  def add_agent(self, name):
    return self.load_plugin(
      plugin_type='agent',
      name=name
    )

# generic plugin loader
  def load_plugin(self, plugin_type, name, class_suffix=None, config_root=None):
  # set class suffix to a sane default
    class_suffix = class_suffix or capwords(plugin_type)

  # dumb-style pluralize for pluggable object types
    plugin_type = plugin_type+'s'
    config_root = config_root or plugin_type

    path = copy.copy(sys.path)
    plugins_custom_path = Config.get('%s.path' % plugin_type)

    path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), plugin_type))
    path.insert(0, '/etc/reacter/%s' % plugin_type)
    path.insert(0, os.path.expanduser('~/.reacter/%s' % plugin_type))

  # add custom plugin paths as most specific search path(s)
    if plugins_custom_path:
      if isinstance(plugins_custom_path, list):
        for a in plugins_custom_path:
          path.insert(0, os.path.expanduser(a))
      else:
        path.insert(0, os.path.expanduser(plugins_custom_path))

  # attempt plugin load
    _file = None
    _path = None
    _description = None

    try:
      (_file, _path, _description) = imp.find_module(name, path)
      plugin_module = imp.load_module(name, _file, _path, _description)
      klass = getattr(plugin_module, Util.camelize(name, suffix=class_suffix))
      store = getattr(self, plugin_type)
      kl = klass(name)
      store.append(kl)
      return kl

    except ImportError as e:
      Util.error('Could not load', class_suffix.lower(), name+':', e.message)
      Util.error('Search path for %s %s:' % (class_suffix.lower(), name))
      for p in path:
        Util.error('  ', os.path.abspath(p))

    finally:
      if _file:
        _file.close()

    return None

  def listen(self):
    self.listening = True

    while self.listening:
      try:
        messages = self.adapter.poll()

      # make this a list if it isn't already
        if not isinstance(messages, list):
          messages = [messages]

      # dispatch all returned messages
        for m in messages:
          self.dispatch_message(m)

      # this poll was successful, we're still connected / successfully reconnected
        self.wait_reconnect = (1,1)

      except adapter.AdapterConnectionFailed as e:
      # emit disconnected message
        self.dispatch_message(Util.get_event_message('disconnected', 'error'))

      # wait then attempt reconnect
        self.wait_connect()
        self.start_connection()
        continue

      except adapter.AdapterConnectionClosed as e:
      # emit disconnected message
        self.dispatch_message(Util.get_event_message('disconnected', 'error'))
        break

      except Exception as e:
        raise adapter.AdapterConnectionFaulted(e)


  def wait_connect(self):
  # wait along the fibonacci sequence to reconnect...
    Util.error('Could not connect to %s adapter, retrying in %ds...' % (self.adapter.name, self.wait_reconnect[1]))
    time.sleep(self.wait_reconnect[0]+self.wait_reconnect[1])

  # max retry wait time
    if self.wait_reconnect[1] < int(Config.get('options.retry_limit') or Util.DEFAULT_RETRY_LIMIT):
      self.wait_reconnect = (self.wait_reconnect[1], self.wait_reconnect[0]+self.wait_reconnect[1])


  def dispatch_message(self, message):
    last_return_value = None

  # do nothing if missing required fields
  #   time
  #   metric
  #   value OR event==true
  #
    if not (
      ('time'   in message.data) and
      ('metric' in message.data) and
      (
        ('value' in message.data) or
        ('event' in message.data and message.data['event'] == True)
      )
    ): return None

  # iterate through all agents, dispatching the message to each of them
  #   process the agents sequentially, passing the output of one agent into the
  #   next one in the chain.
  #   * if the last agent did not return anything, pass in the original message
  #   * if the last agent returned False, pass an empty Message to the next one
  #
    for agent in self.agents:
      if last_return_value == False:
        message = Message()

      last_return_value = agent.received(last_return_value or message)