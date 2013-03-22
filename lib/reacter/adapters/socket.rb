#------------------------------------------------------------------------------#
# Socket Adapter
#
require 'reacter/adapter'
require 'reacter/config'
require 'reacter/util'

class Reacter
  class SocketAdapter < Adapter
    require 'socket'

    class SocketHandler < EM::Connection
      def initialize(*args)
        super
        @callback = args.first
      end

      def receive_data(data)
        @callback.call(data) if @callback
      end
    end

    def connect(args={})
      @addr = @config.get(:address, '0.0.0.0')
      @port = @config.get(:port, 54546)
    end

    def send(message, format=nil)
    # TODO: implement this for relay support
    #   support: host
    #            port
    #            format
    #            timeout
    #
    end

    def poll(&block)
      @server = EM.start_server(@addr, @port, SocketHandler, proc{|data|
        messages = Message.parse(data.chomp)
        block.call(messages) unless messages.empty?
      })
    end

    def disconnect()
      raise AdapterConnectionClosed
    end

  private
    def stdin?()
      @_stdin
    end
  end
end