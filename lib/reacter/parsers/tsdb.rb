require 'reacter/parser'

class Reacter
  class Message
    class TsdbParser < Parser
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

        def dump(message)
          message = message.to_h if message.is_a?(Message)
          return nil unless message.is_a?(Hash)
          return nil unless message[:source]
          return nil unless message[:metric]
          return nil unless message[:value]
          return nil unless message[:time]

          attributes = {
            :host => message[:source]
          }.merge(message[:attributes] || {})

          ([
            'PUT',
            message[:metric],
            (message[:time] / 1000).to_i,
            message[:value],
            attributes.collect{|k,v| "#{k}=#{v}" }.join(' ')
          ].join(' ')).strip
        end
      end
    end
  end
end