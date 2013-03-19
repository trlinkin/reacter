require 'reacter/parsers/default'

class Reacter
  class Message
    class JsonParser < DefaultParser
      class<<self
        require 'json'

        def detected?(message)
          (message[0] == '{' or message[0] == '[')
        end

        def parse(message)
          ([*JSON.load(message)] rescue [])
        end
      end
    end
  end
end