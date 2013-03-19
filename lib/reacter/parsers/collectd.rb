require 'reacter/parsers/default'

class Reacter
  class Message
    class CollectdParser < DefaultParser
      class<<self
        def detected?(message)
          (message[0..6] == 'PUTVAL ')
        end

        def parse(message)
          message = message.split(' ')
          source, plugin, type = message[1].split('/')
          attributes = Hash[message[2].split(';').collect{|i| i.split('=',2) }]
          time, value = message[3].split(':')

          {
            :source     => source,
            :metric     => [plugin, type].join('.'),
            :time       => (time.to_i * 1000),
            :value      => value.to_f,
            :attributes => attributes
          }
        end
      end
    end
  end
end