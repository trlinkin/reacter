#------------------------------------------------------------------------------#
# LoggerAgent
#
require 'reacter/agent'

class Reacter
  class LoggerAgent < Agent
    def initialize()
      super

      case @config.get(:file, 'stdout')
      when 'stderr'
        @stream = STDERR
      when 'stdout'
        @stream = STDOUT
      else
        @stream = File.open(File.expand_path(@config.get(:file)), 'a+')
      end

      @output_format = @config.get(:format)
      puts @output_format.inspect
    end

    def received(message)
      if @output_format.nil?
        line = "logger: [#{message.state or :unknown}] #{message.source}/#{message.metric} = #{message.value}"
      else
        line = Message.dump(message, @output_format)
      end

      @stream.puts(line)
      @stream.flush()

      message
    end
  end
end