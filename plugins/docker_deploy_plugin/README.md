# deploy plugin #

## deploy (event listener) ##

    ---------------------------------------->
        |
        | SIGNAL            
        | post-git-receive-pack      
        ∨                   
        |---------------|
        | deploy plugin |
        |---------------|    

#### example ####

     sudo wflow-install-plugin plugins/docker_buildstep_plugin/ --force
     wflow-trigger-event post-git-receive-pack