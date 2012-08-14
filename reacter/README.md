Overview
========

reacter is a command-line utility for pulling formatted metrics out of a message queue, running comparisons on those metrics to verify whether they meet certain criteria, then performing one or more actions in response to those criteria.  This utility designed to react to ongoing changes in large sets of data.

Reacter connects to a message queue to receive its data.?


Configuration
=============

reacter can be configured using a YAML configuration file.  Supplemental files can be included and merged into the primary configuration to allow for an additive configuration model that can be distributed across multiple files and directories.

By default, reacter will search for the primary configuration file in the following paths.  The first file that is found will be used.  A specific file can be specified directly using the -c flag on the command line.

  /etc/reacter/reacter.yaml
  ~/.reacter/reacter.yaml
  ./reacter.yaml

Supplemental configuration files are used for configuring reacter's agents.  A set of default locations are checked for configurations, but you can specify additional configurations in the primary configuration file.

Given the following primary configuration file:

  reacter:
    myagent:
      config: /path/to/config.yaml

The following files will be found and loaded.  By default, settings in files included later in the process will override ones found earlier on.  All supplemental configuration settings are merged together into one hierarchy.

  /etc/reacter/agents/myagent.yaml
  ~/.reacter/agents/myagent.yaml
  ./agents/myagent.yaml
  /path/to/config.yaml
