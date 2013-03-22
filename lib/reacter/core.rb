require 'eventmachine'
require 'deep_merge'
require 'hashlib'
require 'reacter/message'
require 'reacter/config'
require 'reacter/util'
require 'reacter/adapter'
require 'reacter/agent'

class Reacter
  class Core < EM::Connection
    def initialize(*args)
      super

      @_dispatch_queue = EM::Queue.new
      @_adapters = []
      @_agents = []

      Reacter.load_config(args.first || {})

      load_adapters()
      load_agents()
    end

    def load_adapters()
      adapter_config = Reacter.get('global.adapter', nil)

      if adapter_config
        adapter_config = [adapter_config] if adapter_config.is_a?(Hash)

        adapter_config.each do |adapter|
          type = adapter.get('type')

          if (instance = Adapter.create(type, adapter))
            instance.connect()
            @_adapters << instance
          else
            raise "Adapter '#{type}' not found, exiting"
            exit 1
          end
        end
      else
        Util.fatal("No adapters specified, exiting")
        exit 1
      end
    end

    def load_agents()
      Reacter.get('global.agents.enabled', []).each do |agent|
        agent = Agent.create(agent)
        @_agents << agent if agent
      end

      if @_agents.empty?
        Util.fatal("No agents enabled, exiting")
        exit 1
      end
    end

    def run()
      @_adapters.each do |adapter|
        Util.info("Start listening using #{adapter.type} adapter...")
      end

    # agent message dispatch subprocess
      dispatch = proc do |messages|
        messages.each do |message|
          rv = message

        # send this message to all agents
          @_agents.each do |agent|
            next if rv === false
            rv = agent.received(rv)
          end
        end
      end

    # enter polling loop
      begin
        @_adapters.each do |adapter|
          poller = proc do
            adapter.poll do |messages|
              dispatch.call(messages)
            end
          end

          EM.defer(poller)
        end

      rescue AdapterConnectionFailed => e
        Util.error("Adapter connection failed: #{e.message}")

      rescue AdapterConnectionFaulted => e
        Util.error("Adapter connection error: #{e.message}")

      rescue AdapterConnectionClosed => e
        Util.info("Adapter closed connection")

      end
    end
  end

  class<<self
    def start(config={})
      EM.run do
        reacter = EM.connect('127.0.0.1', 9000, Reacter::Core, config[:options])
        reacter.run()
      end
    end
  end
end