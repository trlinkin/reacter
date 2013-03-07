#------------------------------------------------------------------------------#
# Agent
#
import os
import sys
import time
import imp
from socket import gethostname
import json
from util import Util
from config import Config

class Agent(object):
  def __init__(self, name=None):
    self.name = name
  # agent's config is scoped to reacter.agents.<agent_name>.*
    self.config = Config.get("agents.config.%s" % name, {})

  def log(self, severity='info', *message):
    Util.log('info', ((self.name.upper() or 'AGENT', ':') + message))

  def warn(self, *message):
    self.log('warn', message)

  def error(self, *message):
    self.log('error', message)

  def output(self, *message):
    Util.output(message)


#------------------------------------------------------------------------------#
# Message
#
import datetime

class Message:
  def __init__(self, body={}):
    if isinstance(body, basestring):
      body = json.loads(body)

    self.destination = None
    self.data = Util.dict_merge({
      'raw':        body,
      'time':       int(round(float(datetime.datetime.now().strftime('%s.%f')),3)*1000),
      'attributes': {},
      'metric':     None,
      'source':     None
    }, body)

  # if event is not explicitly stated, and no value is given, assume event=True
    if not 'event' in self.data:
      if not 'value' in self.data:
        self.data['event'] = True


  def get(self, path, default=None):
    return self.data.get(path, default)

  def dump(self):
    return json.dumps(self.data or {})