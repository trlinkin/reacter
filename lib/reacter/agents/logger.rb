#------------------------------------------------------------------------------#
# LoggerAgent
#
require 'reacter/agent'

class Reacter
  class LoggerAgent < Agent
    def received(message)
      Util.info("logger: [#{message.state or :unknown}] #{message.source}/#{message.metric}")
      message
    end
  end
end