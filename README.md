[![Build Status](https://travis-ci.org/pahaz/wflow.svg?branch=master)](https://travis-ci.org/pahaz/wflow)
Shell build tool.

You can use this repo as example for creating you custom user login shells.

# How-to use #

    vagrant up
    vagrant ssh -- -t 'cd /vagrant; sudo make full_clean && sudo make install && sudo make test'

 - Create you custom shell (ex: wflow)
 - Edit Makefile variables for use name `wflow`
 - Write custom plugins-commands for you shell (ex: command_example)
 - bootstrap.sh it.

# How-to setup #

    wget -qO- https://raw.github.com/8iq/wflow/bootstrap.sh | sudo bash
