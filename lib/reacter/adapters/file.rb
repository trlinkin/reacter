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
        @_stdin = true
      else
        @_stdin = false
        @_input = File.open(File.expand_path(@config.get(:filename)), 'r+')
      end
    end

    def send(message)
      false
    end

    def poll(&block)
      loop do
        line = @_input.gets
        yield Message.parse(line)
      end
    end

    def disconnect()
      raise AdapterConnectionClosed
    end

  private
    def stdin?()
      @_stdin
    end
  end
end