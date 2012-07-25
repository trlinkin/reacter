#!/usr/bin/env python
#
# reacter - a utility for consuming and responding to structured input
#
#
#

#------------------------------------------------------------------------------#
# Util
#
import socket
import time
import re

class Util:
  DEFAULT_HOSTNAME=socket.gethostname()
  DEFAULT_PORT=61613


#------------------------------------------------------------------------------#
# Bus
#
import stomp

class Bus:
  def connect(self, host=DEFAULT_DESTINATION, port=Util.DEFAULT_PORT, username=None, password=None, topic=DEFAULT_TOPIC):
    conn = stomp.Connection(
      host_and_ports = [host, port],
      user = username,
      passcode = password
    )
