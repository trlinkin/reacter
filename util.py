#------------------------------------------------------------------------------#
# Util
#
import time
import re
from string import capwords
from copy import deepcopy

class Util:
  DEFAULT_PIDFILE='/var/run/reacter.pid'
  DEFAULT_HOSTNAME="localhost"
  DEFAULT_PORT=61613

  @classmethod
  def parse_destination(self, destination):
    host = self.DEFAULT_HOSTNAME
    port = self.DEFAULT_PORT

    try:
      host, port = destination.split(':')
    except ValueError:
      host = destination
      port = self.DEFAULT_PORT

    return [host, port]

  @classmethod
  def parse_agents(self, agents):
    return agents.split(',')

  @classmethod
  def dict_merge(self, a, b, allow_override=True):
    '''recursively merges dict's. not just simple a['key'] = b['key'], if
    both a and bhave a key who's value is a dict then dict_merge is called
    on both values and the result stored in the returned dictionary.'''

    if not isinstance(b, dict):
      return b

    result = deepcopy(a)

    for k, v in b.iteritems():
      if k in result and isinstance(result[k], dict):
        if allow_override:
          result[k] = self.dict_merge(result[k], v)
      else:
        result[k] = deepcopy(v)

    return result

  @classmethod
  def dict_get(self, root, path, default=None):
    for p in path.split('.'):
      if root.get(p):
        root = root.get(p)
      else:
        return default

    return root

  @classmethod
  def camelize(self, st, prefix='', suffix=''):
    return prefix + capwords(st,'_').replace('_','') + suffix

  @classmethod
  def log(self, message, severity='info'):
    print message

  @classmethod
  def trace(self, message):
    Util.log('TRACE: '+str(message), 'debug')

  @classmethod
  def debug(self, message):
    Util.log(message, 'debug')

  @classmethod
  def info(self, message):
    Util.log(message, 'info')

  @classmethod
  def warn(self, message):
    Util.log(message, 'warn')

  @classmethod
  def error(self, message):
    Util.log(message, 'error')