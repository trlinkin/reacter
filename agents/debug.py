#------------------------------------------------------------------------------#
# DebugAgent
#
import time
from agent import Agent, Message

class DebugAgent(Agent):
  AGENT_TYPE='debug'

  def received(self, message):
    print message.data['raw'].as_string()
