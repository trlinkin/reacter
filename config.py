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

    print yaml.dump(self._config)

# finds and (re)loads the main configuration file
  @classmethod
  def load_main_config(self, config=None):

    path = map(lambda i: os.path.join(i, self.DEFAULT_CONFIG_NAME), self.DEFAULT_CONFIG_PATH)
    if config:
      path.insert(0, config)

    for f in path:
      f = os.path.expanduser(f)

      if os.path.isfile(f):
        self._config = yaml.safe_load(file(f, 'r'))

# processes main config
  @classmethod
  def process_config(self):
  # LOAD supplemental per-agent configurations
    for agent in self.get('agents.enable'):
      agent_config = self.get('agents.%s.config' % agent)

      if agent_config:
        if os.path.isdir(agent_config):
          for i in os.walk(agent_config):
            for j in i[2]:
              if re.match('.*\.yaml', j):
                self.load_supplemental_config(os.path.join(i[0],j))

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
    return Util.dict_get(self._config['reacter'], path, default)