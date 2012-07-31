#------------------------------------------------------------------------------#
# Agent
#
import os
from string import capwords
from socket import gethostname
import stompy
from util import Util

class Agent(object):
  DEFAULT_QUEUE='/queue/monitoring/metrics'
  
  def __init__(self):
    self.agents = []

  def add_agent(self, agent):
    agent_class = getattr(capwords(agent,'_').replace('_','')+'Agent')
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
