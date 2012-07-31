#------------------------------------------------------------------------------#
# Util
#
import time
import re

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