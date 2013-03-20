Gem::Specification.new do |s|
  s.name        = "reacter"
  s.version     = "0.0.4"
  s.date        = "2013-03-18"
  s.summary     = "Reacter monitoring processor"
  s.description = "A utility for consuming, transforming, and routing monitoring data from various sources"
  s.authors     = ["Gary Hetzel"]
  s.email       = "ghetzel@outbrain.com"
  s.files       = [
    "lib/reacter.rb",
    "lib/reacter/adapter.rb",
    "lib/reacter/adapters/amqp.rb",
    "lib/reacter/adapters/file.rb",
    "lib/reacter/agent.rb",
    "lib/reacter/agents/decider.rb",
    "lib/reacter/agents/logger.rb",
    "lib/reacter/agents/relay.rb",
    "lib/reacter/config.rb",
    "lib/reacter/core.rb",
    "lib/reacter/message.rb",
    "lib/reacter/parsers/collectd.rb",
    "lib/reacter/parsers/default.rb",
    "lib/reacter/parsers/graphite.rb",
    "lib/reacter/parsers/json.rb",
    "lib/reacter/parsers/tsdb.rb",
    "lib/reacter/util.rb"
  ]

  s.homepage    = "http://outbrain.github.com/reacter/"
  s.executables = [
    "reacter"
  ]

  %w{
    eventmachine
    deep_merge
    hashlib
  }.each do |g|
    s.add_runtime_dependency g
  end
end