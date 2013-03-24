class Reacter
  class Message
    class Parser
      class<<self
      # implement: determine whether the raw message is in a format this parser
      #            can normalize
        def detected?(message)
          false
        end

      # implement: parse the raw input message, returning an array of Messages
        def parse(message)
          nil
        end

      # take a Message and return the orginal format
        def dump(message)
          nil
        end
      end
    end
  end
end