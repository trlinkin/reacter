class Reacter
  class Message
    class DefaultParser
      class<<self
        def detected?(message)
          false
        end

        def parse(message)
          nil
        end

        def dump(message)
          nil
        end
      end
    end
  end
end