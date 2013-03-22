#------------------------------------------------------------------------------#
# Socket Adapter
#
require 'reacter/adapter'
require 'reacter/config'
require 'reacter/util'

class Reacter
  class HttpAdapter < Adapter
    require 'em-http-server'

    class HttpHandler < EM::HttpServer::Server
      def initialize(*args)
        super
        @callback = args.first
      end

      def process_http_request()
        begin
          @callback.call({
            :method  => @http_request_method.to_sym,
            :host    => @http[:host],
            :path    => @http_request_uri,
            :headers => @http,
            :body    => @http_content,
            :query   => Hash[(@http_query_string || '').split('&').collect{|i|
              i = i.split('=')
              [i[0], i[1]]
            }],
          })
        rescue Exception => e
          puts e
        end

        response = EM::DelegatedHttpResponse.new(self)
        response.status = 200
        response.send_response()
      end
    end


    def connect(args={})
      @addr = @config.get(:address, '0.0.0.0')
      @port = @config.get(:port, 8080).to_i
    end

    def send(message, format=nil)
    # TODO: implement this for relay support
    #   support: method
    #            output format
    #            destination URI (host port path querystring)
    #            HTTPS
    #            authentication (basic, SSL client cert)
    #            timeout
    #
    end

    def poll(&block)
      @server = EM.start_server(@addr, @port, HttpHandler, proc{|data|
        if data
          case data[:method]
          when :GET
            x, op, source, metric, value = data[:path].split('/')

            if op == 'observe' or op.empty?
              messages = Message.parse([{
                :source => (source || data[:query]['source']),
                :metric => (metric || data[:query]['metric']),
                :value  => (value || data[:query]['value'].to_f),
                :time   => (data[:query]['time'] || (Time.now.to_i * 1000)),
                :attributes => data[:query].reject{|k,v|
                  %w{source metric value time}.include?(k)
                }
              }.compact])
            end

          when :POST, :PUT
            messages = Message.parse(data[:body].gsub("\n",''))
          end
        end

        block.call(messages) if messages and not messages.empty?
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