#------------------------------------------------------------------------------#
# FilterAgent
#
require 'reacter/agent'

class Reacter
  class FilterAgent < Agent
    def received(message)
      if @config['sources']
        sources = @config['sources'].keys()

      # fall through if neither default nor our host specifically is named
        return false unless (@config['sources'].include?('default') or @config['sources'].include?(message.source))

      # fall through if the metric is not in either default our the current source's filter
        return false unless (@config['sources']['default'].include?(message.metric) or @config['sources'][message.source].include?(message.metric))
      end

      return message
    end
  end
end
