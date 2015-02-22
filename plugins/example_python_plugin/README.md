# example python plugin #

## printenv (command) ##

    ---------------------------------------->
        |
        | COMMAND
        | printenv      
        ∨                   
        |-----------------------|
        | example python plugin |
        |-----------------------|    

#### example ####

     sudo wflow-install-plugin plugins/example_python_plugin/ --force
     wflow printenv -v

## error (command) ##

    ------------------------------------->
        |
        | COMMAND            
        | error      
        ∨                   
        |-----------------------|
        | example python plugin |
        |-----------------------|    

#### example ####

     sudo wflow-install-plugin plugins/example_python_plugin/ --force
     wflow error -v

## example (event listener) ##

    ---------------------------------------->
        |
        | SIGNAL            
        | example      
        ∨                   
        |-----------------------|
        | example python plugin |
        |-----------------------|    

#### example ####

     sudo wflow-install-plugin plugins/example_python_plugin/ --force
     wflow-trigger-event example awdawd=22 test=113
