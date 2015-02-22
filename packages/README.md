# W DEPLOY #

DEPLOY:

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


# CHANGELOG #

## 0.3.0 ##

 - rename `interface` to `abc`
 - change command interface `AbstractCommand(app, app_parsed_options)` -> `AbstractCommand(event_manager, env)`
 - init `wdeploy`
 - add `write_message_for_user(message)` to `AbstractCommand`
 - change plugin load `load(manager)` -> `load(command_manager, event_manager, env)`
 - remove `Manager`
 - add `make_managers_and_load_them_from_plugin_modules` factory function
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
