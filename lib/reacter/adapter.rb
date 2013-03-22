#------------------------------------------------------------------------------#
# Adapter
#
require 'eventmachine'
require 'reacter/message'
require 'reacter/config'
require 'reacter/util'

class AdapterConnectionFailed < Exception; end
class AdapterConnectionFaulted < Exception; end
class AdapterConnectionClosed < Exception; end

class Reacter
  class Adapter
    attr :config
    attr :type

    def initialize(config=nil)
      @config = (config || Reacter.get('global.adapter', {}))
      @type = @config.get('type')
      Util.info("Loading adapter #{@type}...")
    end

  # implement: connect to the data source
    def connect(args={})
      false
    end

  # implement: send a message suitable for consumption by an instance of reacter
  #            in listen mode
    def send(message, format=nil)
      false
    end

  # implement: poll for a new message and return it
    def poll(&block)
      false
    end

  # implement: manual disconnect / cleanup
    def disconnect()
      raise AdapterConnectionClosed
    end

    class<<self
      def create(type, config=nil)
        if type
          begin
            require "reacter/adapters/#{type}"
            rv = (Reacter.const_get("#{type.capitalize}Adapter").new(config))
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