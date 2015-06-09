# W SHELL #

definitions:

 - *event* - The signal that indicates a specific action stage (beginning, end of key points).
 - *command* - User-initiated action. An important difference between the events of the commands is that the command can be initiated by the user, and the events no.

hierarchy:

 - `EventManager` - program interface for work with events.
 - `CommandManager` - program interface for work with commands.
 - `Core` - facade for work with commands. Used as unix login shell and command batch utility. 

# W DEPLOY #

deploy process:

 1. BUILDER_LOADER select BUILDER (founded on some STACK like 'Ubuntu 14.10')
 2. BUILDER make the new container image with the build project (by using BUILDPACK like 'heroku-buildpack-python') and make RUNNER
 3. CONTAINER_MANAGER run one or multiple container image instance(s)

hierarchy:

    BUILDER_LOADER
     - get_builder_for_project
       |
    BUILDER (founded on STACK)
     - build (use BUILDPACK)
     - get_runner
     - get_latest_build_version
       |
    CONTAINER_MANAGER
     - start_stopped - 
     - stop - 
     - kill - 
     - restart - 
     - run - 
     - recreate - 
     - remove_stopped - 

# TODO: FEATURES #

 - `EventManager` add support complex events: example {'git-receive-pack', 'deploy'} for 'nginx_plugin' - BAD! 

# CHANGELOG #

## 0.4.0 ##

 - many incompatible changes
 - new managers system: `CommandManager` with `run_command` and `EventManager` with `trigger_event`
 - `EnvStack` now used as `env` object
 - release `wdeploy`
 - changes in pre/post run command events: used fixed event names (`pre-run-command` and `post-run-command`)

## 0.3.0 ##

 - rename `interface` to `abc`
 - change command interface `AbstractCommand(app, app_parsed_options)` -> `AbstractCommand(event_manager, env)`
 - init `wdeploy` (alpha interfaces)
 - add `write_message_for_user(message)` to `AbstractCommand`
 - change plugin load `load(manager)` -> `load(command_manager, event_manager, env)`
 - remove `Manager`
 - add `load_managers_from_plugins` factory function
 - add `command_manager` to `AbstractCommand`

## 0.2.4 ##

 - add `is_hidden_for_command_list` method for `Command` - use in interactive mode

# WRITE PLUGIN #

You can write two types of plugins:
 - simple hook (any language)
 - python plugin

### python plugin ###

#### logging ####

Default logging levels: 
 - debug, info - for developers. debug uses for deep debugging. 
 - warning - for user information. (deprecated, please use `write_message_for_user`)
 - error - for user and developers. in debug mode print stack trace.
 - critical - not uses.
