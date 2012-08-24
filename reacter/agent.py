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
from config import Config

class Agent(object):
  def __init__(self, name=None):
    self.name = name
  # agent's config is scoped to reacter.<agent_name>.*
    self.config = Config.get(name, {})

  def log(self, *message):
    Util.log('info', ((self.name.upper() or 'AGENT', ':') + message))


#------------------------------------------------------------------------------#
# Message
#
import datetime

class Message:
  def __init__(self, frame=None):
    self.init(frame)

  def init(self, frame=None):
    self.destination = None
    self.data = {
      'raw':        frame,
      'time':       int(round(float(datetime.datetime.now().strftime('%s.%f')),3)*1000),
      'attributes': {},
    }

    if frame:
      self.set_from_frame(frame)

  def set_from_frame(self, frame):
    self.data = dict(self.data.items() + frame.headers.items())
    self.data['value'] = frame.body
