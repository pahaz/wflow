STACK_URL ?= https://github.com/pahaz/herokuish.git

PLATFORM_USERNAME ?= wflow

all:
	# Type "make install" to install.

install: docker buildstep

docker:
	# http://docs.docker.com/installation/ubuntulinux/
	@command -v docker > /dev/null || curl -sSL https://get.docker.io/ubuntu/ | sudo sh
	# Warning: The docker group (or the group specified with the -G flag) is root-equivalent; see Docker Daemon Attack Surface details.
	egrep -i "^docker" /etc/group || groupadd docker
	usermod -aG docker ${PLATFORM_USERNAME}
	sleep 2 # give docker a moment i guess

buildstep:
	@docker images | grep herokuish || (git clone ${STACK_URL} /tmp/buildstep && cd /tmp/buildstep && make && cd - && rm -rf /tmp/buildstep)
