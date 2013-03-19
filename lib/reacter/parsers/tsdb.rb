require 'reacter/parsers/default'

class Reacter
  class Message
    class TsdbParser < DefaultParser
      class<<self
        def detected?(message)
          return (message.upcase[0..4] == 'PUT ')
        end

        def parse(message)
          message = message.split(' ')

          {
            :metric     => message[1],
            :time       => (message[2].to_i * 1000),
            :value      => message[3].to_f,
            :attributes => Hash[message[4..-1].collect{|i| i.split('=',2) }]
          }
        end
      end
    end
  end
end