#------------------------------------------------------------------------------#
# RelayAgent
#
require 'reacter/agent'
require 'reacter/adapter'

class Reacter
  class RelayAgent < Agent
    def initialize()
      super

      if @config['type']
        @_adapter = Adapter.create(@config['type'], @config)
        raise "Could not create relay adapter #{@config['type']}" unless @_adapter
        @_adapter.connect()
      end

      @_signature = Util.signature()
    end

    def received(message)
      if @_adapter
        message[:relayed_from] = @_signature unless (@config['transparent'] === true)
        @_adapter.send(message, @config['format'])
      else
        Util.warn("relay: Message received without an active relay adapter, dropping")
        return false
      end

      return message
    end
  end
end