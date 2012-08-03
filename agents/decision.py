#------------------------------------------------------------------------------#
# DecisionAgent
#
import re
import yaml
from agents import Agent, Message

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
    self.threshold_file = './reacter.yaml'
    self.yaml = yaml.safe_load(open(threshold_file, 'r'))

  # TODO: set this from the config
    self.valid_states = DEFAULT_STATES

  def received(self, message):
    sources = self.yaml['thresholds']['sources']
    rules = {}

  # add all matching rules for all matching sources
    for source in sources.keys():
      if source == 'default' or re.match(source, message.data['source']):
        for rule in sources[source].keys():
          if re.match(rule, message.data['metric']):
            rules[rule] = sources[source]][rule]

  # for each applicable rule
    for rule in rules.keys():
      add_observation(rule, message)


  def add_observation(rule, message):
    source = message.data['source']
    metric = message.data['metric']
    value  = message.data['value']

  # create data structures if they do not exist
    if not self.observations[source]:
      self.observations[source] = {}
      
    if not self.observations[source][metric]:
      self.observations[source][metric] = {}


    observations = self.observations[source][metric]
    hits = rule.get('hits') or 1


  # do value check
    state, violation = get_state(value, rule)

  # further adjust hits for the specific state we're in
    try:
      hits = rule['states'][self.valid_states[state]]['hits']
    except Exception:
      pass

  # set last violation state
    observations['last_state'] = observations['state']
    observations['state'] = state

  # increment checks
    observations['stats']['checks'] += 1

  # determine current violation state
    if state == 0:
      observations['breach_count'] = 0
      observations['clear_count'] += 1

    # only succeed after n passing checks
      if observations['clear_count'] >= hits:
        observations['clear_count'] = 0
        observations['in_violation'] = False
        perform_action(observations)

    else:
      observations['breach_count'] += 1
      observations['clear_count'] = 0

    # only violate every n breaches
      if observations['breach_count'] >= hits:
        observations['breach_count'] = 0
        observations['in_violation'] = True
        perform_action(observations)