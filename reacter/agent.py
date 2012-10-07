#------------------------------------------------------------------------------#
# Agent
#
import os
import sys
import time
import imp
from socket import gethostname
import yaml
from util import Util
from config import Config

class Agent(object):
  def __init__(self, name=None):
    self.name = name
  # agent's config is scoped to reacter.agents.<agent_name>.*
    self.config = Config.get(name, {})

  def log(self, *message):
    Util.log('info', ((self.name.upper() or 'AGENT', ':') + message))


#------------------------------------------------------------------------------#
# Message
#
import datetime

class Message:
  def __init__(self, body={}):
    self.destination = None
    self.data = Util.dict_merge({
      'raw':        body,
      'time':       int(round(float(datetime.datetime.now().strftime('%s.%f')),3)*1000),
      'attributes': {},
    }, body)

    self.data['event'] = self.data.has_key('value')