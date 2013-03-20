require 'reacter/util'
require 'reacter/config'

class Reacter
  class Message
    require 'hashlib'
    DEFAULT_SOURCE_NAME='default'
    DEFAULT_FORMAT=:json

    def initialize(message={})
      @_data = {
        :raw        => message,
        :time       => (Time.now.to_i * 1000),
        :attributes => {},
        :metric     => nil,
        :source     => DEFAULT_SOURCE_NAME
      }.merge(message)

      if not @_data.has_key?(:event) and not @_data.has_key?(:value)
        @_data[:event] = true
      else
        @_data[:event] = false
      end
    end

    def to_h
      @_data
    end

    def [](key)
      @_data[key.to_sym]
    end

    def []=(key, value)
      @_data[key.to_sym] = value
    end

    def method_missing(name, *args)
      @_data[name.to_sym] or args.first
    end

    class<<self
      def load_parsers()
        unless defined?(@@_parsers)
          @@_parsers = {}

        # load and initialize parsers
          Dir[File.join(File.dirname(__FILE__), 'parsers', '*.rb')].each do |i|
            i = File.basename(i,'.rb')
            require "reacter/parsers/#{i}"
            @@_parsers[i.to_sym] = Message.const_get("#{i.capitalize}Parser")
          end
        end
      end

      def dump(message, format=nil)
        load_parsers() unless defined?(@@_parsers)

        if @@_parsers
          format = DEFAULT_FORMAT unless format

          if @@_parsers.has_key?(format.to_sym)
            return @@_parsers[format.to_sym].dump(message)
          end
        end

        return nil
      end

      def parse(body)
        load_parsers()

      # split strings into lines
        body = body.lines if body.is_a?(String)
        messages = []

        if body.respond_to?(:each)
          body.each do |message|
          # strings need to be detected and parsed
            if message.is_a?(String)
              next if message.strip.chomp.empty?

            # use first parser that claims it can handle this string
              @@_parsers.each do |name, parser|
                if parser.detected?(message)
                  #Util.debug("Using parser #{name}")
                  m = parser.parse(message)
                  (m.is_a?(Array) ? messages += m : messages << m)
                  next
                end
              end

          # hashes go directly into the stack
            elsif message.is_a?(Hash)
              messages << message
            end
          end

        end

        messages.collect{|i| Message.new(i) }
      end
    end
  end
end