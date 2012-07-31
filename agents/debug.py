import time
from agent import Agent

class DebugAgent(Agent):
  AGENT_TYPE='debug'

  def __init__(self, name=AGENT_TYPE):
    self.name = name
    self.count = 0

  def received(self, message):
    self.count = self.count + 1
    
    #if (self.count % 10) == 0:
    print str(time.time()) + ': ' + str(self.count)
