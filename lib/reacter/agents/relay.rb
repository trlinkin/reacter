#------------------------------------------------------------------------------#
# RelayAgent
#
require 'reacter/agent'
require 'reacter/adapter'

class Reacter
  class RelayAgent < Agent
    def initialize()
      super

      @_adapters = []
      @_signature = Util.signature(object_id.to_s(16).upcase)

      @config = (@config.is_a?(Hash) ? [@config] : [*@config])

      @config.each do |c|
        if c['type']
          adapter = Adapter.create(c['type'], c)
          adapter.connect()
          @_adapters << adapter
        end
      end

      @_adapter_cycle = @_adapters.cycle.each
    end

    def received(message)
      adapter = @_adapter_cycle.next

      if adapter
        message[:relayed_from] = @_signature unless (adapter.config['transparent'] === true)
        adapter.send(message, adapter.config['format'])
      else
        Util.warn("relay: Message received without an active relay adapter, dropping")
        return false
      end

      return message
    end
  end
end