#------------------------------------------------------------------------------#
# DebugAgent
#
import time
from reacter.agent import Agent, Message

class DebugAgent(Agent):
  AGENT_TYPE='debug'

  def received(self, message):
    print message.data['raw'].as_string()
