#------------------------------------------------------------------------------#
# LoggerAgent
#
require 'reacter/agent'

class Reacter
  class LoggerAgent < Agent
    def received(message)
      Util.info("LOGGER: [#{message.state or :unknown}] #{message.source}/#{message.metric}")
    end
  end
end