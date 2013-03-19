#------------------------------------------------------------------------------#
# DeciderAgent
#
require 'reacter/agent'

class Reacter
  class DeciderAgent < Agent
    class EmitAlert < Exception; end

    STATES=[:okay, :warning, :critical]
    COMPARISONS=%w{not is above below}

    def initialize()
      super

      @_state_names = {}
      STATES.each_index do |i|
        @_state_names[STATES[i]] = i
      end

      @_alerts = {}
    end

    def received(message)
    # early exit conditions
      return false unless @config
      return false unless @config['sources']
      return false unless message.metric
      unless message.source
        return false unless @config['sources']['any']
      end

    # build effective configuration rule for this message
      general = (@config['sources']['any'][message.metric] or {} rescue {})
      specific = (@config['sources'][message.source][message.metric] or {} rescue {})
      rule = specific.deep_merge!(general)

    # quit early for empty rules
      return false if rule.empty?

    # quit early for invalid rules
      return false unless (rule['threshold'] and rule['actions'])

    # passthrough mode
    #   if in passthrough mode, all messages that are present in the configuration
    #   will be passed regardless of state.  this is useful in conjunction with
    #   the relay agent to offload the decision making to another reacter instance
      return message if (@config['options'] and @config['options']['passthrough'])

    # default return value: false
      rv = false

    # initialize in-memory alert tracking (per source, per metric)
      @_alerts[message.source] ||= {}
      @_alerts[message.source][message.metric] ||= ({
        :count           => 1,
        :last_state      => nil,
        :last_seen       => nil,
        :new_alert       => false,
        :has_ever_failed => false
      })

    # get current state of this message according to the rule
      state, comparison = state_of(message, rule)

      begin
        # a non-okay alert has occurred, this metric can now be said to have failed
          unless state == :okay
            @_alerts[message.source][message.metric][:has_ever_failed] = true
          end

        # the state has changed, reset counter
          if @_alerts[message.source][message.metric][:last_state] != state
            @_alerts[message.source][message.metric][:new_alert] = true
            @_alerts[message.source][message.metric][:count] = 1
          end

          hits = ((rule['threshold'][state.to_s][hits] rescue rule['hits']) or rule['hits'] or 1).to_i
          persist = ((rule['threshold'][state.to_s]['persist'] === true) rescue false)

        # only raise every n alerts
          if @_alerts[message.source][message.metric][:count] >= hits
          # raise the alert if it's new or if we're persistently reminding of alerts
            if @_alerts[message.source][message.metric][:new_alert] or persist
            # only emit if this metric has ever failed
              if @_alerts[message.source][message.metric][:has_ever_failed]
                raise EmitAlert
              end
            end
          end


      rescue EmitAlert
        message[:state] = state
        message[:comparison] = comparison
        message[:check_value] = (rule['threshold'][state][comparison] rescue nil)
        message[:alerted_at] = Time.now.to_i

        rv = message

      # alert is emitted, it's not new anymore
        @_alerts[message.source][message.metric][:new_alert] = false

      ensure
        @_alerts[message.source][message.metric][:count] += 1
        @_alerts[message.source][message.metric][:last_state] = state
        @_alerts[message.source][message.metric][:last_seen] = Time.now.to_i
      end

      return rv
    end


  private

    def state_of(message, rule)
      worst_state = 0
      comparison = nil

    # for each state, add all breached states
      rule['threshold'].each do |state, check|
        state = state.to_sym

        check.each do |comp, test|
          if compare(message.value, comp, test)
          # this breached state is worse than what we've seen, make it the worst
            if @_state_names[state] > worst_state
              worst_state = @_state_names[state]
              comparison = comp
            end
          end
        end
      end

      return [STATES[worst_state], comparison]
    end

    def compare(value, comparison, test)
      case comparison.to_sym
      when :not
        return (value != test)
      when :is
        return (value == test)
      when :above
        return (value > test)
      when :below
        return (value < test)
      else
        return false
      end
    end
  end
end


# {"complements"=>"df-var.df_complex-used",
#   "attributes"=>{
#     "owner"=>"This Guy <tguy@outbrain.com>",
#     "description"=>"",
#     "neon"=>{"url"=>"http://localhost:5000/alert/new"}},
#   "actions"=>{
#     "exec"=>["~/Dropbox/Outbrain/reacter-notify"]},
#   "threshold"=>{
#     "warning"=>{
#       "below"=>"5%"}}}
