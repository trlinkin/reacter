require 'reacter/parser'

class Reacter
  class Message
    class GraphiteParser < Parser
      class<<self
      # Graphite
      #   |metric-----|value|epoch----|
      # => metric.name 12345 123456789
        def detected?(message)
          (message =~ /^[\w\.]+ [\d\.\-]+ \d+$/ ? true : false)
        end

        def parse(message)
          message = message.split(' ')

          {
            :metric     => message[0],
            :value      => message[1].to_f,
            :time       => (message[2].to_i * 1000)
          }
        end

        def dump(message)
          message = message.to_h if message.is_a?(Message)
          return nil unless message.is_a?(Hash)
          #return nil unless message[:source]
          return nil unless message[:metric]
          return nil unless message[:value]
          return nil unless message[:time]

          "#{message[:metric]} #{message[:value]} #{(message[:time] / 1000).to_i}".strip
        end
      end
    end
  end
end