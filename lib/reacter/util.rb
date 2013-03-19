require 'reacter/config'

class Reacter
  class Util
    class<<self
      require 'logger'

      @@_logger = {
        :default => Logger.new(STDOUT)
      }

      def log(message, severity=:info, log=:default)
        @@_logger[log] = Logger.new(STDOUT) unless @@_logger[log]
        @@_logger[log].send(severity, [*message].join(' '))
      end

      def info(message, log=:default)
        log(message, :info, log)
      end

      def debug(message, log=:default)
        log(message, :debug, log)
      end

      def warn(message, log=:default)
        log(message, :warn, log)
      end

      def error(message, log=:default)
        log(message, :error, log)
      end

      def fatal(message, log=:default)
        log(message, :fatal, log)
      end
    end
  end
end