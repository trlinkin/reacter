class Reacter
  class<<self
    require 'yaml'

    DEFAULT_CONFIG={
      'global' => {
        'searchpath' => ['~/.reacter', '/etc/reacter'],
        'configs' => [
          '~/.reacter/reacter.yaml',
          '/etc/reacter/reacter.yaml'
        ]
      }
    }

    def load_config(config={})
      @_config = DEFAULT_CONFIG
      default_path = DEFAULT_CONFIG.get('global.configs')

    # load from default paths
      default_path.each do |path|
        _load_file(path)
      end

    # load any supplemental configs
      @_config.get('global.searchpath').each do |dir|
      # adapters
        adapter = @_config.get('global.adapter.type')
        _load_file(File.join(dir, 'adapters', "#{adapter}.yaml")) if adapter

      # agents
        @_config.get('global.agents.enabled', []).each do |agent|
          _load_file(File.join(dir, 'agents', "#{agent}.yaml"))
        end
      end

    # load from any new paths that were loaded
      (@_config.get('global.configs') - default_path).each do |path|
        _load_file(path)
      end

      @_config = config.deep_merge!(@_config, {
        :merge_hash_arrays => true
      })
    end

    def [](key)
      get(key)
    end

    def []=(key, value)
      set(key, value)
    end

    def get(path, default=nil)
      @_config.get(path, default)
    end

    def set(path, value)
      @_config.set(path, value)
    end

    def dump_config()
      @_config
    end


  private
    def _load_file(path)
      path = File.expand_path(path)

      if File.exists?(path)
        Util.info("Loading configuration #{path}...")
        yaml = YAML.load(File.read(path))

        @_config = yaml.deep_merge!(@_config, {
          :merge_hash_arrays => true
        })
      end
    end
  end
end