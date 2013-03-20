#------------------------------------------------------------------------------#
# DeciderAgent
#
require 'reacter/agent'

class Reacter
  class DeciderAgent < Agent
    class EmitAlert < Exception; end
  # local memory persistence mechanism for state tracking
    class MemoryPersist
      class<<self
        def setup(config={})
          @_alerts = {}
        end

        def init(source, metric)
        # initialize in-memory alert tracking (per source, per metric)
          @_alerts[source] ||= {}
          @_alerts[source][metric] ||= DEFAULT_PERSISTENCE_OBJECT
        end

        def get(source, metric, key)
          @_alerts[source][metric][key] rescue nil
        end

        def set(source, metric, key, value)
          (@_alerts[source][metric][key] = value) rescue nil
        end
      end
    end

  # redis persistence mechanism for shared state tracking
    class RedisPersist
      require 'redis'
      require 'hiredis'
      require 'msgpack'

      class<<self
        def setup(config={})
          @_redis = Redis.new({
            :host   => config.get(:host),
            :port   => config.get(:port),
            :path   => config.get(:socket),
            :driver => config.get(:driver, :hiredis).to_sym
          })

          @_ttl = config.get('ttl', 600)
        end

        def init(source, metric)
          DEFAULT_PERSISTENCE_OBJECT.each do |key, value|
            @_redis.multi do
              @_redis.set("#{source}:#{metric}:#{key}", value.to_msgpack)
            end
          end
        end

        def get(source, metric, key)
          MessagePack.unpack(@_redis.get("#{source}:#{metric}:#{key}"))
        end

        def set(source, metric, key, value)
          k = "#{source}:#{metric}:#{key}"
          @_redis.set(k, value.to_msgpack)
          @_redis.expire(k, @_ttl)
        end
      end
    end

    STATES=[:okay, :warning, :critical]
    COMPARISONS=%w{not is above below}
    DEFAULT_PERSISTENCE='memory'
    DEFAULT_PERSISTENCE_OBJECT=({
      :count           => 1,
      :last_state      => nil,
      :last_seen       => nil,
      :new_alert       => false,
      :has_ever_failed => false,
      :total_value     => nil
    })

    def initialize()
      super

      @_state_names = {}
      STATES.each_index do |i|
        @_state_names[STATES[i]] = i
      end

      @_persistence = DeciderAgent.const_get(@config.get('options.persistence.type', DEFAULT_PERSISTENCE).capitalize+'Persist')
      @_persistence.setup(@config.get('options.persistence', {}))
    end

    def received(message)
    # early exit conditions
      return false unless @config
      return false unless @config['sources']
      return false unless message.metric
      unless message.source
        return false unless @config['sources']['any']
      end

      s = message.source
      m = message.metric

    # build effective configuration rule for this message
      general = (@config['sources']['any'][m] or {} rescue {})
      specific = (@config['sources'][s][m] or {} rescue {})
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

    # initialize persistence for this source/metric
      persist_init(s,m)

    # get current state of this message according to the rule
      state, comparison = state_of(message, rule)

      begin
        # a non-okay alert has occurred, this metric can now be said to have failed
          unless state == :okay
            persist_set(s,m, :has_ever_failed, true)
          end

        # the state has changed, reset counter
          if persist_get(s,m, :last_state) != state
            persist_set(s,m, :new_alert, true)
            persist_set(s,m, :count, 1)
          end

          hits = ((rule['threshold'][state.to_s][hits] rescue rule['hits']) or rule['hits'] or 1).to_i
          persist = ((rule['threshold'][state.to_s]['persist'] === true) rescue false)

        # only raise every n alerts
          if persist_get(s,m, :count) >= hits
          # raise the alert if it's new or if we're persistently reminding of alerts
            if persist_get(s,m, :new_alert) or persist
            # only emit if this metric has ever failed
              if persist_get(s,m, :has_ever_failed)
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
        persist_set(s,m, :new_alert, false)

      ensure
        persist_set(s,m, :count, persist_get(s,m, :count) + 1)
        persist_set(s,m, :last_state, state)
        persist_set(s,m, :last_seen, Time.now.to_i)
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

    def persist_init(source, metric)
      @_persistence.init(source, metric)
    end

    def persist_get(source, metric, key)
      @_persistence.get(source, metric, key)
    end

    def persist_set(source, metric, key, value)
      @_persistence.set(source, metric, key, value)
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
