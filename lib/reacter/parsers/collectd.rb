require 'reacter/parser'

class Reacter
  class Message
    class CollectdParser < Parser
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

        def dump(message)
          message = message.to_h if message.is_a?(Message)
          return nil unless message.is_a?(Hash)
          return nil unless message[:source]
          return nil unless message[:metric]
          return nil unless message[:value]
          return nil unless message[:time]

          ([
            'PUTVAL',
            "#{message[:source]}/#{message[:metric]}",
            (message[:attributes] || {}).collect{|k,v| "#{k}=#{v}"}.join(';'),
            "#{(message[:time] / 1000).to_i}:#{message[:value]}"
          ].join(' ')).strip
        end
      end
    end
  end
end