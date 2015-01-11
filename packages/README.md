# CHANGELOG #

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
 - warning - for user information.
 - error - for user and developers. in debug mode print stack trace.
 - critical - not uses.
