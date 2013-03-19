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
      @_adapter = nil
      @_agents = []

      Reacter.load_config()

      load_adapters()
      load_agents()
    end

    def load_adapters()
      adapter_config = Reacter.get('global.adapter', nil)

      if adapter_config
        type = adapter_config.get('type')

        @_adapter = Adapter.create(type)

        if @_adapter
          @_adapter.connect()
        else
          raise "Adapter '#{type}' not found, exiting"
          exit 1
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
      Util.info("Start listening using #{@_adapter.type} adapter...")


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
        @_adapter.poll do |messages|
          @_dispatch_queue.push(messages)
          @_dispatch_queue.pop(dispatch)
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
    def start()
      EM.run do
        reacter = EM.connect('127.0.0.1', 9000, Reacter::Core)
        reacter.run()
      end
    end
  end
end