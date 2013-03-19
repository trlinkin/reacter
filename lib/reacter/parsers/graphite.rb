require 'reacter/parsers/default'

class Reacter
  class Message
    class GraphiteParser < DefaultParser
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
      end
    end
  end
end