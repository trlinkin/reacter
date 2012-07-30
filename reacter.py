#!/usr/bin/env python
#
# reacter - a utility for consuming and responding to structured input
#
#
#

#------------------------------------------------------------------------------#
# Util
#
import time
import re

class Util:
  DEFAULT_PIDFILE='/var/run/reacter.pid'
  DEFAULT_HOSTNAME="localhost"
  DEFAULT_PORT=61613

  @classmethod
  def parse_destination(self, destination):
    host = self.DEFAULT_HOSTNAME
    port = self.DEFAULT_PORT

    try:
      host, port = destination.split(':')
    except ValueError:
      host = destination
      port = self.DEFAULT_PORT

    return [host, port]

  @classmethod
  def parse_agents(self, agents):
    return agents.split(',')

#------------------------------------------------------------------------------#
# Agent
#
from socket import gethostname
import stompy
from string import capwords

class Agent(object):
  DEFAULT_QUEUE='/queue/monitoring/metrics'
  
  def __init__(self):
    self.agents = []

  def add_agent(self, agent):
    agent_class = globals()[capwords(agent,'_').replace('_','')+'Agent']
    self.agents.append(agent_class())

  def connect(self, host=Util.DEFAULT_HOSTNAME, port=Util.DEFAULT_PORT, username=None, password=None, queue=DEFAULT_QUEUE):
    self.queue_name = queue
    self.conn = stompy.simple.Client(
      host=host,
      port=int(port)
    )

    try:
      self.conn.connect(
        username=username,
        password=password,
        clientid='%s-%s-%s' % ('reacter', gethostname(), os.getpid())
      )

    except Exception as e:
      print "Could not connect: %s" % e.message
      return False

    return True

  def send(self, message):
    self.conn.put(message, destination=self.queue_name)

  def process(self, queue):
    self.conn.subscribe(queue, ack='auto')
    self.running = True

    while self.running:
      message = self.conn.get(block=True)
      
      self.dispatch_message(message)


  def dispatch_message(self, message):
    #print "Message received, dispatching to agent(s): "

    for agent in self.agents:
      #print agent.name+': '
      agent.received(message)

class DebugAgent(Agent):
  AGENT_TYPE='debug'

  def __init__(self, name=AGENT_TYPE):
    self.name = name
    self.count = 0

  def received(self, message):
    self.count = self.count + 1
    
    if (self.count % 10) == 0:
      print str(time.time()) + ': ' + str(self.count)


#------------------------------------------------------------------------------#
# Reacter
#
import os
import sys
from optparse import OptionParser

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
        self.queue.process(queue=self.opts.queue)

    else:
      sys.exit(1)

reacter = Reacter()
reacter.start()
