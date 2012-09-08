#!/usr/bin/env python
#
# reacter - a utility for consuming and responding to structured input
#
#
#

#------------------------------------------------------------------------------#
# Reacter
#
import os
import sys
from optparse import OptionParser
from util import Util
from core import Core
from config import Config

class Reacter:
  def __init__(self):
    self.setup()

  def setup(self):
    self.setup_cli_args()
    Config.load(self.opts.config)
    self.process_config()
    self.process_cli_args()

  def setup_cli_args(self):
    p = OptionParser()

    p.add_option("-c", "--config",
      dest='config',
      help='The location of the configuration YAML to load',
      metavar='FILE')

    p.add_option("-A", "--adapter",
      dest='adapter',
      help='The name of the adapter to use for sending and receiving data',
      metavar='ADAPTER',
      default=None)

    p.add_option("-a", "--agents",
      dest='agents',
      help='A comma-separated list of agents to enable to process received messages',
      metavar='AGENT[,AGENT ...]',
      default='')

    p.add_option('-p', '--pid',
      dest='pidfile',
      help='The location of the PID file',
      metavar='PIDFILE',
      default=Util.DEFAULT_PIDFILE)
    
    p.add_option('-R', '--no-retry',
      dest='no_retry_connection',
      help='Do not automatically attempt to reconnect to the message queue on failed attempts',
      action="store_true"
    )

    (self.opts, self.args) = p.parse_args()

  def process_config(self):
    self.agents = Config.get('agents.options.enabled', [])

  def process_cli_args(self):
    cli_agents = Util.parse_agents(self.opts.agents)

    if cli_agents:
      self.agents = cli_agents

  def initialize_daemon(self):
    # pid = open(self.opts.pidfile, 'w')
    # pid.write(str(os.getpid())+'\n')
    # pid.close()
    return None

  def start(self):
  # setup daemon-specific things
    self.initialize_daemon()

  # initialize core
    self.core = Core()

  # add the backend adapter
    self.core.add_adapter(self.opts.adapter or Config.get('adapter.name'))

    for agent in self.agents:
      if len(agent) > 0:
        Util.info('Registering agent:', agent)
        self.core.add_agent(agent)

    if Config.get('agents.options.chain'):
      Util.info('Chain mode activated: messages will be sequentially delivered to agents in the order %s' % ' -> '.join(self.agents))

  # connect to message queue
    if self.core.connect(
      retry=not(self.opts.no_retry_connection)
    ):

    # send message via standard input
      if not sys.stdin.isatty():
        self.core.send(sys.stdin.read())

      else:
        self.core.listen()

    else:
      sys.exit(1)