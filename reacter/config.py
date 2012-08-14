#------------------------------------------------------------------------------#
# Config
#
import os
import re
import yaml
from util import Util

class Config:
  DEFAULT_CONFIG_PATH=['./', '~/.reacter', '/etc/reacter']
  DEFAULT_CONFIG_NAME='reacter.yaml'

  _config = {}

  @classmethod
  def load(self, config=None):
    self.load_main_config(config)
    self.process_config()


# finds and (re)loads the main configuration file
  @classmethod
  def load_main_config(self, config=None):
  # build list of possible config file paths to search for
    path = map(lambda i: os.path.join(i, self.DEFAULT_CONFIG_NAME), self.DEFAULT_CONFIG_PATH)

    if config:
      path.insert(0, config)

  # attempt to load config from paths, first match wins
    for f in path:
      f = os.path.expanduser(f)

      if os.path.isfile(f):
        self._config = yaml.safe_load(file(f, 'r'))
        break


# processes main config
  @classmethod
  def process_config(self):
  # LOAD supplemental per-agent configurations
    for agent in self.get('agents.options.enabled'):
      agent_custom = self.get('agents.%s.config' % agent)

    # get a list of custom agent config paths to include
      if agent_custom:
        if isinstance(agent_custom,str):
          agent_custom = [agent_custom]

    # look in well known locations
      agent_configs = [
        ('/etc/reacter/agents/%s.yaml' % agent),
        os.path.expanduser('~/.reacter/agents/%s.yaml' % agent),
        './agents/%s.yaml' % agent,
      ]

    # add custom paths as more specific than default paths
      agent_configs.append(agent_custom)


    # attempt to load supplemental configs from:
    #   /etc/reacter/agents/<agent>.yaml
    #   ~/.reacter/agents/<agent>.yaml
    #   ./agents/<agents>.yaml
    #   <path in config> (if supplied)
    #
      for agent_config in agent_configs:
        if agent_config:
        # recursively include .yaml files in a supplied directory
          if os.path.isdir(agent_config):
            for i in os.walk(agent_config):
              for j in i[2]:
                if re.match('.*\.yaml', j):
                  self.load_supplemental_config(os.path.join(i[0],j))

        # include a specific file
          elif os.path.isfile(agent_config):
            self.load_supplemental_config(agent_config)


# validates and loads a supplemental config, merging it into the main config
#   supplemental config values will replace main config values if the main config
#   specifies options.config.allow_override=true
  @classmethod
  def load_supplemental_config(self, config):
    config = os.path.expanduser(config)

    if os.path.isfile(config):
      Util.debug('Loading supplemental config %s...' % config)
      try:
        sc = yaml.safe_load(file(config, 'r'))
        self._config = Util.dict_merge(self._config, sc, self.get('options.config.allow_override', True))

      except IOError as e:
        Util.warn('Could not load supplemental configuration: %s' % e.message)  

    else:
      Util.warn('Could not find supplemental configuration %s, skipping' % config)

    return False

  @classmethod
  def get(self, path, default=None):
    path = re.sub('^reacter\.', '', path)
    return Util.dict_get(self._config['reacter'], path, default)