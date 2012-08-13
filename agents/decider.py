#------------------------------------------------------------------------------#
# DeciderAgent
#
import os
import sys
import re
import yaml
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
        'state':                None,
        'last_state':           None,
        'in_violation':         False,
        'check_count':          0,
        'breach_count':         0,
        'clear_count':          0
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

  # not a good plan....
    message.data['rule'] = Util.get_rule_id(source, metric, state, comparison)

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

      # only set state/last_state when violation changes occur
        observations['last_state'] = observations.get('state')
        observations['state'] = state

        self.dispatch_alert(observations, rule, message)

    else:
      observations['breach_count'] += 1
      observations['clear_count'] = 0


    # only violate every n breaches
      if observations['breach_count'] >= hits:
        observations['breach_count'] = 0
        observations['in_violation'] = True

      # only set state/last_state when violation changes occur
        observations['last_state'] = observations.get('state')
        observations['state'] = state

        self.dispatch_alert(observations, rule, message)

    return observations


  def dispatch_alert(self, observation, rule, message):
    for action in rule.get('actions').keys():
    # NOT OKAY
      if observation['in_violation']:
      # if the last state was different than the current one or if we're just persistently nagging about alerts...
        if observation['last_state'] != observation['state'] or rule.get('persistent'):
          self.call_handler(action, rule['actions'][action], message)

    # OKAY
      else:
      # if the last state was different than the current one or if we're shouting that everything's okay...
        if observation['last_state'] != observation['state'] or rule.get('persistent_ok'):
          self.call_handler(action, rule['actions'][action], message)

  def call_handler(self, name, action, message):
    #try:
    klass = getattr(sys.modules[__name__], Util.camelize(name, suffix='Handler'))
    i = klass()
    i.call(action, message) 

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
  def call(self, action, m):
    return False


#------------------------------------------------------------------------------#
import subprocess

class ExecHandler(DecisionHandler):
  def call(self, action, m):
    cmd = None

    print '%s %s/%s: value %f %s threshold of %f' % (m.data['state'].upper(), m.data['source'], m.data['metric'], float(m.data['value'] or 0.0), m.data['comparison'], float(m.data['threshold'] or 0.0))

    if isinstance(action, dict):
      cmd = action.get('command')
    else:
      cmd = action

    if cmd:
    # setup environment
      env = os.environ.copy()
      env["REACTER_SOURCE"] = str(m.data['source'])
      env["REACTER_METRIC"] = str(m.data['metric'])
      env["REACTER_THRESHOLD"] = str(m.data['threshold'])
      env["REACTER_COMPARISON"] = str(m.data['comparison']).upper()
      env["REACTER_STATE"] = str(m.data['state']).upper()
      env["REACTER_RULE"] = str(m.data['rule'])
      env["REACTER_VALUE"] = str(m.data['value'])

    # export global generic params as envvars
    #   if config['thresholds'].get('params'):
    #     for k in config['thresholds']['params']:
    #       env['REACTER_PARAM_'+k.upper()] = str(config['thresholds']['params'][k])

    # # override/augment them with params from lower levels
    #   if condition.get('params'):
    #     for k in condition['params']:
    #       env['REACTER_PARAM_'+k.upper()] = str(condition['params'][k])

    # execute
      subprocess.Popen(cmd, env=env, shell=True, stdin=None, stdout=None, stderr=None)


#------------------------------------------------------------------------------#
import yaml

class PostHandler(DecisionHandler):
  def call(self, action, m):
    output = action.get('type') or 'yaml'
    #http = action.get('')

    #if isinstance()
    # POST output (yaml/json) -> URL