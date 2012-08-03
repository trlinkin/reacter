#------------------------------------------------------------------------------#
# Agent
#
import os
import sys
import imp
from string import capwords
from socket import gethostname
import stompy
from util import Util

class Agent(object):
  DEFAULT_QUEUE='/queue/monitoring/metrics'
  
  def __init__(self):
    self.agents = []

  def add_agent(self, agent):
    path = sys.path
    path.insert(1, '/etc/reacter/agents')
    path.insert(1, os.path.expanduser('~/.reacter/agents'))
    path.insert(1, './agents')

    try:
      (_file, _path, _description) = imp.find_module(agent, path)
      agent_module = imp.load_module(agent, _file, _path, _description)
      agent_class = getattr(agent_module, capwords(agent,'_').replace('_','')+'Agent')
      self.agents.append(agent_class())
    finally:
      _file.close()

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
      );

    except Exception as e:
      print "Could not connect: %s" % e.message
      return False

    return True

  def send(self, message, headers=None):
    self.conn.put(message,
      destination=self.queue_name,
      conf=headers)

  def process(self, queue):
    self.conn.subscribe(queue, ack='auto')
    self.running = True

    while self.running:
      message = self.conn.get(block=True)
      
      self.dispatch_message(message)


  def dispatch_message(self, frame):
    #print "Message received, dispatching to agent(s): "

    for agent in self.agents:
      agent.received(Message(frame))


#------------------------------------------------------------------------------#
# Message
#

class Message:
  def __init__(self, frame=None):
    self.init(frame)

  def init(self, frame=None):
    self.destination = None
    self.data = {
      'raw':         frame,
      'source':      None,
      'metric':      None,
      'value':       None,
      'threshold':   None,
      'state':       None
    }

    if frame:
      self.set_from_frame(frame)

  def set_from_frame(self, frame):
    self.data = dict(self.data.items() + frame.headers.items())
    self.data['value'] = frame.body
