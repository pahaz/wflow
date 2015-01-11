# git plugin #

## git-receive ##

    |----------|         |----------------------------|
    | (SOURCE) | --ssh-> | git plugin | (copy SOURCE) | 
    | git push |         |----------------------------|
    |----------|         |                            |
                         | SIGNAL                     | SIGNAL
                         | pre-git-receive-pack       | post-git-receive-pack
                         ∨                            ∨

### signals ###

 - pre-git-receive-pack
 - post-git-receive-pack

## git-upload ##

    |-----------|         |----------------------------|
    | (SOURCE)  | <-ssh-- | git plugin | (copy SOURCE) | 
    | git clone |         |----------------------------|
    | git pull  |
    |-----------|         |                            |
                          | SIGNAL                     | SIGNAL
                          | pre-git-upload-pack        | post-git-upload-pack
                          ∨                            ∨

### signals ###

 - pre-git-upload-pack
 - post-git-upload-pack
