#------------------------------------------------------------------------------#
# AMQP Adapter
#
require 'reacter/adapter'
require 'reacter/config'
require 'reacter/util'

class Reacter
  class AmqpAdapter < Adapter
    require 'amqp'

    DEFAULT_QUEUENAME='reacter'
    DEFAULT_TIMEOUT=3

    def connect(args={})
      @_errback = proc do
        raise AdapterConnectionFailed
      end

      @_connection = AMQP.connect({
        :host     => @config.get(:hostname, 'localhost'),
        :port     => @config.get(:port, 5672),
        :username => @config.get(:username, 'guest'),
        :password => @config.get(:password, 'guest'),
        :vhost    => @config.get(:vhost, '/'),
        :timeout  => @config.get(:timeout, DEFAULT_TIMEOUT),
        :on_tcp_connection_failure => @_errback
      })

      @_channel  = AMQP::Channel.new(@_connection)
      @_queue    = @_channel.queue(@config.get(:queue, DEFAULT_QUEUENAME), {
        :auto_delete => @config.get(:autodelete, true),
        :arguments => {
          'x-message-ttl' => @config.get(:ttl)
        }.compact
      })

      @_exchange = @config.get(:exchange, '')
    end

    def send(message, format=nil)
      false
    end

    def poll(&block)
      @_queue.bind(@_exchange).subscribe do |payload|
        yield Message.parse(payload)
      end
    end

    def disconnect()
      raise AdapterConnectionClosed
    end
  end
end