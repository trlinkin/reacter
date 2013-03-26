#------------------------------------------------------------------------------#
# RunnerAgent
#
require 'reacter/agent'

class Reacter
  class RunnerAgent < Agent
    def received(message)
      general =  (Reacter[%W{agents decider sources any #{message.metric}}] || {})
      specific = (Reacter[%W{agents decider sources #{message.source} #{message.metric}}] || {}) if message.source
      decider_config = specific.deep_merge!(general)

      unless decider_config.empty?
        actions = [*decider_config.get('actions.exec', [])]

        actions.each do |action|
          if action.is_a?(String)
            action = {
              'command' => action
            }
          end

          xenv = action.get('environment', {}).collect{|k,v|
            ["REACTER_#{k.upcase}", v]
          }

          message.to_h.reject{|k,v| k.to_sym == :raw }.each_recurse{|k,v,path|
            xenv << ["REACTER_#{path.collect{|i| i.upcase }.join('_')}", v.to_s]
          }
          xenv = Hash[xenv]

          puts xenv.inspect
        end
      end

      return message
    end
  end
end