# git plugin #

Plugin for work with git CVS. Support two command: `git-receive-pack` and `git-upload-pack`

## git-receive-pack command ##

    +----------+         +----------------------------+
    | (SOURCE) | --ssh-> | git plugin | (copy SOURCE) | 
    | git push |         +----------------------------+
    +----------+                                |
                                                | SIGNAL
                                                | git-receive-pack
                                                ∨    

### signals ###

 - *git-receive-pack* - trigger after source received
 - *git-receive-pack context* : `dns_name`, `repo_local_path`

## git-upload-pack command ##

    +-----------+         +----------------------------+
    | (SOURCE)  | <-ssh-- | git plugin | (copy SOURCE) | 
    | git clone |         +----------------------------+
    | git pull  |
    +-----------+                                |
                                                 | SIGNAL
                                                 | git-upload-pack
                                                 ∨

### signals ###

 - *git-upload-pack* - trigger after source uploaded
 - *git-upload-pack context* : `dns_name`, `repo_local_path`
