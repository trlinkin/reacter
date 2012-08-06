#------------------------------------------------------------------------------#
# DecisionAgent
#
import re
import yaml
import zlib
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

class DecisionAgent(Agent):
  DEFAULT_STATES=['okay', 'warning', 'critical']

  def __init__(self):
    self.observations = {}
    self.config()

  def config(self):     
    #if not threshold_file:
    #  raise Exception('Must specify a ThresholdFile configuration file (yaml)')
    try:
      self.threshold_file = '/home/ghetzel/src/github/outbrain/reacter/agents/reacter.yaml'
      self.yaml = yaml.safe_load(open(self.threshold_file, 'r'))
    except IOError:
      self.yaml = {
        'thresholds': {
          'sources': {}
        }
      }

  # TODO: set this from the config
    self.valid_states = self.DEFAULT_STATES


  def received(self, message):
    sources = self.yaml['thresholds']['sources']
    rules = {}

  # add all matching rules for all matching sources
    for source in sources.keys():
      if source == 'default' or re.match(source, message.data['source']):
        for rule in sources[source].keys():
          if re.match(rule, message.data['metric']):
            rules[rule] = sources[source][rule]

  # for each applicable rule
    for rule in rules.keys():
      observation = self.add_observation(rules[rule], message)
      print observation


  def add_observation(self, rule, message):
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

    if comparison:
    # further adjust hits for the specific state we're in
      try:
        hits = rule['states'][state]['hits']
      except Exception:
        pass

    # set last violation state
      observations['last_state'] = observations.get('state')
      observations['state'] = state

    # not a good plan....
      observations['rule_id'] = abs((zlib.crc32('%s-%s-%s-%s' % (source, metric, state, comparison)) & 0xffffffff))

    # increment checks
      observations['check_count'] += 1

    # determine current violation state
      if state == 'okay':
        observations['breach_count'] = 0
        observations['clear_count'] += 1

      # only succeed after n passing checks
        if observations['clear_count'] >= hits:
          observations['clear_count'] = 0
          observations['in_violation'] = False
          #print_struct(observations)

      else:
        observations['breach_count'] += 1
        observations['clear_count'] = 0

      # only violate every n breaches
        if observations['breach_count'] >= hits:
          observations['breach_count'] = 0
          observations['in_violation'] = True
          #print_struct(observations)

      return observations

    return None

  def get_state(self, value, rule):
  # for all non-okay states (ordered by most-to-least severe)
    for state in self.valid_states[::-1][:-1]:
      state_rule = rule.get(state)

    # if a rule for this state exists...
      if state_rule:        
      # ...and value is above the 'max':
        if state_rule.get('max') and float(value) > float(state_rule.get('max')):
          return (state, 'max')

      # ...or equal to the 'is':
        elif state_rule.get('is') and float(value) == float(state_rule.get('is')):
          return (state, 'is')

      # ...or less than the 'min':
        elif state_rule.get('min') and float(value) < float(state_rule.get('min')):
          return (state, 'min')

    return (None,None)

  def print_struct(self, s, m , v, o):
    print "%s/%s: %s %d B/C=%d/%d (%d)" % (s, m, o.data['state'].upper(), v, o['breach_count'], o['clear_count'], o['check_count'])
