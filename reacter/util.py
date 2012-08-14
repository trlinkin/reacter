#------------------------------------------------------------------------------#
# Util
#
import time
import re
import zlib
from string import capwords
from copy import deepcopy
from socket import gethostname

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
    a = agents.split(',')
    a[:] = [x for x in a if len(x) > 0]

    if len(a) == 0:
      return []

    return a

  @classmethod
  def dict_merge(self, a, b, allow_override=True):
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
  def log(self, severity, *message):
  # stringify all arguments and join them with a space
    print ' '.join(map(lambda i: str(i), list(message[0])))

  @classmethod
  def trace(self, *message):
    Util.log('debug', message)

  @classmethod
  def debug(self, *message):
    Util.log('debug', message)

  @classmethod
  def info(self, *message):
    Util.log('info', message)

  @classmethod
  def warn(self, *message):
    Util.log('warn', message)

  @classmethod
  def error(self, *message):
    Util.log('error', message)

  @classmethod
  def get_rule_id(self, source, metric, state, comparison):
    return abs((zlib.crc32('%s-%s-%s-%s' % (source, metric, state, comparison)) & 0xffffffff))

  @classmethod
  def get_event_message(self, event, state='okay', value=1):
    from agent import Message
    message = Message()

    message.data['source'] = gethostname()
    message.data['threshold'] = 1
    message.data['comparison'] = 'is'
    message.data['state'] = state
    message.data['rule'] = Util.get_rule_id(gethostname(), 1, state, 'is')
    message.data['value'] = value
    message.data['metric'] = 'events.reacter.queue.%s' % event

    return message
