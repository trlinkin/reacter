#------------------------------------------------------------------------------#
# DeciderAgent
#
import sys
import re
import yaml
import zlib
from util import Util
from config import Config
from agent import Agent, Message

# --8<----------------------------------------------------------------------8<--
# MESSAGE
# expires:0
# timestamp:1344000286678
# metric:system.cpu.cpu-0.idle
# destination:/queue/monitoring/metrics
# priority:4
# source:titan.nyc.outbrain.com
# x-client:127.0.1.1
# message-id:ID:amq-01.lab-46618-1343998646040-2:4:-1:1:1
#
# 1234
# -->8---------------------------------------------------------------------->8--

class DeciderAgent(Agent):
  DEFAULT_STATES=['okay', 'warning', 'critical']

  def __init__(self, name):
    super(DeciderAgent,self).__init__(name)
    self.observations = {}

  # TODO: set this from the config
    self.valid_states = self.DEFAULT_STATES


  def received(self, message):
    sources = self.config['sources']

    print sources
    rules = {}

  # add all matching rules for all matching sources
    for source in sources.keys():
      if source == 'all' or re.match(source, message.data['source']):
        for rule in sources[source].keys():
          if re.match(rule, message.data['metric']):
            rules[rule] = sources[source][rule]

  # for each applicable rule
    for rule in rules.keys():
      observation = self.evaluate_rule(rules[rule], message)


  def evaluate_rule(self, rule, message):
    source = message.data['source']
    metric = message.data['metric']
    value  = message.data['value']

  # create data structures if they do not exist
    if not self.observations.get(source):
      self.observations[source] = {}
      
    if not self.observations[source].get(metric):
      self.observations[source][metric] = {
        'state':        None,
        'check_count':  0,
        'breach_count': 0,
        'clear_count':  0
      }

    observations = self.observations[source][metric]
    hits = rule.get('hits') or 1

  # do value check
    state, comparison = self.get_state(value, rule)

    message.data['state'] = state
    message.data['comparison'] = comparison

  # set threshold for the current state/comparison
  # okay has no threshold
    if not state == 'okay':
      try:
        message.data['threshold'] = float(rule['when'][state][comparison])
      except KeyError:
        pass
    
  # further adjust hits for the specific state we're in
    try:
      hits = rule['when'][state]['hits']
    except KeyError:
      pass

  # set last violation state
    observations['last_violation_state'] = observations.get('in_violation')
    observations['state'] = state

  # not a good plan....
    message.data['rule'] = abs((zlib.crc32('%s-%s-%s-%s' % (source, metric, state, comparison)) & 0xffffffff))

  # increment checks
    observations['check_count'] += 1

  # if state is okay...
    if state == 'okay':
      observations['breach_count'] = 0
      observations['clear_count'] += 1

    # only succeed after n passing checks
      if observations['clear_count'] >= hits:
        observations['clear_count'] = 0
        observations['in_violation'] = False
        self.dispatch_alert(observations, rule, message)

    else:
      observations['breach_count'] += 1
      observations['clear_count'] = 0

    # only violate every n breaches
      if observations['breach_count'] >= hits:
        observations['breach_count'] = 0
        observations['in_violation'] = True
        self.dispatch_alert(observations, rule, message)

    return observations


  def dispatch_alert(self, observation, rule, message):
    for action in rule.get('actions').keys():
    # NOT OKAY
      if observation['in_violation']:
      # if the last violation was clean or if we're just persistently nagging about alerts...
        if not observation['last_violation_state'] or rule.get('persistent'):
          self.call_handler(action, message)

    # OKAY
      else:
      # if the last violation was dirty or if we're shouting that everything's okay...
        if observation['last_violation_state'] or rule.get('persistent_ok'):
          self.call_handler(action, message)

  def call_handler(self, name, message):
    #try:
    klass = getattr(sys.modules[__name__], Util.camelize(name, suffix='Handler'))
    i = klass()
    i.call(message) 

    #except Exception as e:
    #  pass


  def get_state(self, value, rule):
  # for all non-okay states (ordered by most-to-least severe)
    for state in self.valid_states[::-1][:-1]:
      state_rule = rule['when'].get(state)

    # if a rule for this state exists...
      if state_rule:   
      # ...and value is not equal to:
        if state_rule.get('not') and float(value) != float(state_rule.get('not')):
          return (state, 'not')

      # ...or is equal to:
        elif state_rule.get('is') and float(value) == float(state_rule.get('is')):
          return (state, 'is')

      # ...and value is above the 'above':
        elif state_rule.get('above') and float(value) > float(state_rule.get('above')):
          return (state, 'above')

      # ...or less than the 'below':
        elif state_rule.get('below') and float(value) < float(state_rule.get('below')):
          return (state, 'below')

    return ('okay',None)

  def print_struct(self, s, m , v, o):
    print "%s/%s: %s %d B/C=%d/%d (%d)" % (s, m, o.data['state'].upper(), v, o['breach_count'], o['clear_count'], o['check_count'])

#------------------------------------------------------------------------------#
# DecisionHandler
#
class DecisionHandler:
  def call(self, m):
    return False


#------------------------------------------------------------------------------#
class ExecHandler(DecisionHandler):
  def call(self, m):
    print '%s %s/%s: value %f %s threshold of %f' % (m.data['state'].upper(), m.data['source'], m.data['metric'], float(m.data['value'] or 0.0), m.data['comparison'], float(m.data['threshold'] or 0.0))
    return True
