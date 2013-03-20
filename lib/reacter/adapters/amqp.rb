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

    def connect(args={})
      @_connection = AMQP.connect({
        :host     => @config.get(:hostname, 'localhost'),
        :port     => @config.get(:port, 5672),
        :username => @config.get(:username, 'guest'),
        :password => @config.get(:password, 'guest'),
        :vhost    => @config.get(:vhost, '/')
      })

      @_channel  = AMQP::Channel.new(@_connection)
      @_queue    = @_channel.queue(@config.get(:queue, DEFAULT_QUEUENAME), {
        :auto_delete => @config.get(:autodelete, true)
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