require 'reacter/parser'

class Reacter
  class Message
    class JsonParser < Parser
      class<<self
        require 'json'

        def detected?(message)
          (message[0] == '{' or message[0] == '[')
        end

        def parse(message)
          ([*JSON.load(message)] rescue [])
        end

        def dump(message)
          message = message.to_h if message.is_a?(Message)
          return nil unless message.is_a?(Hash)
          JSON.dump(message)
        end
      end
    end
  end
end