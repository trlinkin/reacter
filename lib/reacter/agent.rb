#------------------------------------------------------------------------------#
# Agent
#
require 'reacter/message'
require 'reacter/config'
require 'reacter/util'

class Reacter
  class Agent
    attr :config
    attr :type

    def initialize()
      @type = self.class.name.sub('Agent', '').split('::').last.downcase
      @config = Reacter.get("agents.#{@type}", {})
      Util.info("Loading agent #{@type}...")
    end

    def received(message)
      false
    end

    class<<self
      def create(type)
        if type
          begin
            agentpath = Reacter['global.agents.path']
            $: << File.expand_path(agentpath) if agentpath

            require "reacter/agents/#{type}"
            rv = (Reacter.const_get("#{type.capitalize}Agent").new())
            return rv

          rescue LoadError
            nil
          end
        end

        nil
      end
    end
  end
end