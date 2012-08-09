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
    Config.load()

  def setup_cli_args(self):
    p = OptionParser()

    p.add_option("-H", "--hostname",
      dest='stomp_server',
      help='The STOMP server to connect to',
      metavar='HOST[:PORT]',
      default="%s:%s" % (Util.DEFAULT_HOSTNAME, Util.DEFAULT_PORT))

    p.add_option("-q", "--queue",
      dest='queue',
      help='The name of the message queue to receive messages from',
      metavar='QUEUE',
      default=Core.DEFAULT_QUEUE)

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

    p.add_option('-m', '--message',
      dest='send_message',
      help='A single message to add to the queue',
      metavar='MESSAGE',
      default=None
    )

    p.add_option('-F', '--header',
      action='append',
      dest='send_message_headers',
      help='A header to add to an outgoing message',
      metavar='NAME VALUE',
      default=None,
      nargs=2
    )

    (self.opts, self.args) = p.parse_args()

    self.agents = Util.parse_agents(self.opts.agents)

  # handle multiple -F arguments
    headers = self.opts.send_message_headers
    self.opts.send_message_headers = {}
    
    if headers:
      for h in headers:
        self.opts.send_message_headers[h[0]] = h[1]
    
    (self.stomp_host, self.stomp_port) = Util.parse_destination(self.opts.stomp_server)

  def initialize_daemon(self):
    # pid = open(self.opts.pidfile, 'w')
    # pid.write(str(os.getpid())+'\n')
    # pid.close()
    return None

  def send(self, message, headers=None):
    self.core.send(message, headers)

  def start(self):
  # setup daemon-specific things
    self.initialize_daemon()

  # initialize agents
    self.core = Core()

    for agent in self.agents:
      if len(agent) > 0:
        Util.info('Registering agent %s' % agent)
        self.core.add_agent(agent)

  # connect to message queue
    if self.core.connect(
      host=self.stomp_host,
      port=self.stomp_port):

      if self.opts.send_message:
        self.send(self.opts.send_message, self.opts.send_message_headers)

      else:
        self.core.process(queue=self.opts.queue)

    else:
      sys.exit(1)

reacter = Reacter()
reacter.start()
