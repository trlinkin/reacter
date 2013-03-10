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
      'source':     'default'
    }, body)

  # if event is not explicitly stated, and no value is given, assume event=True
    if not 'event' in self.data:
      if not 'value' in self.data:
        self.data['event'] = True


  def get(self, path, default=None):
    return self.data.get(path, default)


  def dump(self):
    return json.dumps(self.data or {})


  @classmethod
  def parse(self, body):
    messages = []
    rv = []

  # load all input messages
    if isinstance(body, basestring):
      body = body.split('\n')

    if isinstance(body, list):
      for line in body:
        if len(line.strip()) == 0:
          continue

        try:
        # handle a direct JSON object
          if line[0] == '{':
            messages.append(json.loads(line))

        # handle an array of metrics
          elif line[0] == '[':
            m = json.loads(line)

            if not isinstance(m,list):
              for i in m:
                messages.append(i)

        # OpenTSDB formatted string
          elif line.upper()[0:4] == 'PUT ':
            line = line.split(' ')

          # expose TSDB tags as attributes
            attrs = {}
            for a in line[4:-1]:
              a = a.split('=', 1)
              attrs[a[0]] = a[1]

            messages.append({
              'metric':     line[1],
              'time':       (int(line[2])*1000),
              'value':      float(line[3]),
              'attributes': attrs
            })

        # Graphite formatted string
          elif len(line.split(' ')) == 3:
            line = line.split(' ')
            messages.append({
              'metric': line[0],
              'value':  float(line[1]),
              'time':   (int(line[2])*1000)
            })

        # collectd formatted string
          elif line[:6] == 'PUTVAL':
          # will require configuration to point to the collectd types.db to
          # correctly deconstruct metrics into the correct metrics

          # * read types db(s)
          # * split up line
          # * append one message for each value associated with the type-instance
          #   of this line

          # BUT FOR NOW LET'S JUST HACK IT OUT SO WE CAN SEE *SOMETHING*
            line = line.split(' ')

            metric = line[1].split('/')

          # source name is the first component
            source = metric[0]

          # metric name is the rest
            metric = '.'.join(metric[1:])

            timeval = line[3].split(':')
            time = (float(timeval[0])*1000)
            value = float(timeval[1])

            messages.append({
              'source': source,
              'metric': metric,
              'value':  value,
              'time':   time
            })

        except Exception, e:
          Util.error("Could not parse message %s" % (body[:20] + '..') if len(body) > 20 else body, ": %s" % e)
          continue

  # create Message objects
    for message in messages:
      try:
        rv.append(Message(message))
      except Exception, e:
        Util.error("Could not construct Message object:", e)
        continue

    return rv