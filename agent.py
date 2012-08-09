#------------------------------------------------------------------------------#
# Agent
#
import os
import sys
import time
import imp
from socket import gethostname
import stompy
from util import Util

class Agent(object):
  def __init__(self, name=None):
    self.name = name
    self.config = Config.get('agents.%s' % name, {})


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
      'state':       None,
      'comparison':  None,
      'rule':        None
    }

    if frame:
      self.set_from_frame(frame)

  def set_from_frame(self, frame):
    self.data = dict(self.data.items() + frame.headers.items())
    self.data['value'] = frame.body
