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
import signal
from optparse import OptionParser
from util import Util
from core import Core
from config import Config

class Reacter:
  def __init__(self):
    self.running = False
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

    p.add_option('-s', '--send',
      dest='send_mode',
      help='Operate in send mode, pushing a message into an adapter',
      action="store_true"
    )

    (self.opts, self.args) = p.parse_args()

  def process_config(self):
    self.agents = Config.get('agents.enabled', [])

  def process_cli_args(self):
    cli_agents = Util.parse_agents(self.opts.agents)

    if cli_agents:
      self.agents = cli_agents

  def initialize_daemon(self):
    signal.signal(signal.SIGINT, self.signal_handler)

    # pid = open(self.opts.pidfile, 'w')
    # pid.write(str(os.getpid())+'\n')
    # pid.close()

    return None

  def start(self):
    #if self.opts.send_mode:
    # mute logger output of severity < warning

  # initialize core
    self.core = Core()

  # set the backend adapter
    self.core.set_adapter(self.opts.adapter or Config.get('adapter.type'))

  # add all agents
    for agent in self.agents:
      if len(agent) > 0:
        Util.info('Registering agent:', agent)
        self.core.add_agent(agent)

    if Config.get('agents.chain'):
      Util.info('Chain mode activated: messages will be sequentially delivered to agents: %s' % ' -> '.join(self.agents))

  # connect to message queue
    if self.core.connect(
      retry=not(self.opts.no_retry_connection),
      sender=self.opts.send_mode
    ):

    # we're running now
      self.running = True

    # send mode (via standard input)
      if self.opts.send_mode:
        self.core.send(sys.stdin.read())

    # listen mode (default)
      else:
      # setup daemon-specific things
        self.initialize_daemon()

        while self.running:
          #try:
            self.core.listen()

          # except Exception, e:
          #   import traceback, os.path
          #   tb = traceback.extract_stack()[-1]

          #   Util.error('[!!]', type(e).__name__.split('.')[-1],
          #     'in %s:%s' %(os.path.basename(tb[0]), str(tb[1]))+':',
          #     (e.message or ''))

    else:
      sys.exit(1)

  def signal_handler(self, number, frame):
    self.running = False
    Util.debug('SIGNAL', number, frame)

    if number == signal.SIGINT:
      self.core.disconnect()

    sys.exit(0)