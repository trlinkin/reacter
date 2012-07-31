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
from agent import Agent

class Reacter:
  def __init__(self):
    self.setup()

  def setup(self):
    self.setup_cli_args()

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
      default=Agent.DEFAULT_QUEUE)

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

    (self.opts, self.args) = p.parse_args()

    self.agents = Util.parse_agents(self.opts.agents)
    (self.stomp_host, self.stomp_port) = Util.parse_destination(self.opts.stomp_server)

  def initialize_daemon(self):
    pid = open(self.opts.pidfile, 'w')
    pid.write(str(os.getpid())+'\n')
    pid.close()

  def send(self, message):
    self.queue.send(message)

  def start(self):
  # setup daemon-specific things
    self.initialize_daemon()

  # initialize agents
    self.queue = Agent()

    for agent in self.agents:
      if len(agent) > 0:
        self.queue.add_agent(agent)

  # connect to message queue
    if self.queue.connect(
      host=self.stomp_host,
      port=self.stomp_port):

      if self.opts.send_message:
        self.send(reacter.opts.send_message)
      else:
        print "Starting..."
        print "Connected to %s:%s" % (self.stomp_host, self.opts.queue)
        self.queue.process(queue=self.opts.queue)

    else:
      sys.exit(1)

reacter = Reacter()
reacter.start()
