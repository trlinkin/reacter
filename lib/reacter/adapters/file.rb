#------------------------------------------------------------------------------#
# Standard Input Adapter
#
require 'reacter/adapter'
require 'reacter/config'
require 'reacter/util'

class Reacter
  class FileAdapter < Adapter
    def connect(args={})
      if @config.get(:filename) == 'stdin'
        @_input = STDIN
      else
        if (readfile = (@config.get('filename') || @config.get('file.read')))
          @_input = File.open(File.expand_path(readfile), 'r+')
        end
      end

      if (writefile = @config.get('file.write'))
        @_output = File.open(File.expand_path(writefile), 'a')
      end
    end

    def send(message, format=nil)
      if defined?(@_output)
        message = Message.dump(message, format)
        @_output.puts(message) if message
        @_output.flush()
      else
        Util.warn("file: Attempting to send without a valid output file handle")
      end
    end

    def poll(&block)
      if @_input
        loop do
          disconnect() if @_input.eof?
          line = @_input.gets
          yield Message.parse(line)
        end
      else
        Util.warn("file: Attempting to poll without a valid input file handle")
      end
    end

    def disconnect()
      raise AdapterExit
    end

  private
    def stdin?()
      @_stdin
    end
  end
end