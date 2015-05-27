# settings begin

PLATFORM_VERSION = master

PLATFORM_NAME ?= wflow
PLATFORM_PLUGIN_INSTALLER_COMMAND ?= ${PLATFORM_NAME}-install-plugin
PLATFORM_PLUGIN_DEACTIVATOR_COMMAND ?= ${PLATFORM_NAME}-deactivate-plugin
PLATFORM_PLUGIN_ACTIVATOR_COMMAND ?= ${PLATFORM_NAME}-activate-plugin
PLATFORM_TRIGGER_EVENT_COMMAND ?= ${PLATFORM_NAME}-trigger-event

PLATFORM_USERNAME ?= wflow
PLATFORM_DATA_PATH ?= /home/${PLATFORM_USERNAME}

PLATFORM_PATH ?= /usr/local/bin/${PLATFORM_NAME}
PLATFORM_PLUGIN_INSTALLER_PATH ?= /usr/local/bin/${PLATFORM_PLUGIN_INSTALLER_COMMAND}
PLATFORM_PLUGIN_DEACTIVATOR_PATH ?= /usr/local/bin/${PLATFORM_PLUGIN_DEACTIVATOR_COMMAND}
PLATFORM_PLUGIN_ACTIVATOR_PATH ?= /usr/local/bin/${PLATFORM_PLUGIN_ACTIVATOR_COMMAND}
PLATFORM_EVENT_TRIGGER_PATH ?= /usr/local/bin/${PLATFORM_TRIGGER_EVENT_COMMAND}

PLATFORM_PLUGINS_PATH ?= /var/lib/${PLATFORM_NAME}/plugins
PLATFORM_VENV_PATH ?= /var/lib/${PLATFORM_NAME}/venv

# settings end

define CONFIG
[DEFAULT]
PLATFORM_NAME = ${PLATFORM_NAME}
PLATFORM_PLUGIN_INSTALLER_COMMAND = ${PLATFORM_PLUGIN_INSTALLER_COMMAND}
PLATFORM_PLUGIN_DEACTIVATOR_COMMAND = ${PLATFORM_PLUGIN_DEACTIVATOR_COMMAND}
PLATFORM_PLUGIN_ACTIVATOR_COMMAND = ${PLATFORM_PLUGIN_ACTIVATOR_COMMAND}
PLATFORM_TRIGGER_EVENT_COMMAND = ${PLATFORM_TRIGGER_EVENT_COMMAND}

PLATFORM_USERNAME = ${PLATFORM_USERNAME}
PLATFORM_DATA_PATH = ${PLATFORM_DATA_PATH}

PLATFORM_PATH = ${PLATFORM_PATH}
PLATFORM_PLUGINS_PATH = ${PLATFORM_PLUGINS_PATH}
PLATFORM_VENV_PATH = ${PLATFORM_VENV_PATH}
PLATFORM_PLUGIN_INSTALLER_PATH = ${PLATFORM_PLUGIN_INSTALLER_PATH}
PLATFORM_PLUGIN_DEACTIVATOR_PATH = ${PLATFORM_PLUGIN_DEACTIVATOR_PATH}
PLATFORM_PLUGIN_ACTIVATOR_PATH = ${PLATFORM_PLUGIN_ACTIVATOR_PATH}
PLATFORM_EVENT_TRIGGER_PATH = ${PLATFORM_EVENT_TRIGGER_PATH}
endef

export CONFIG

CURRENT_USER_ID = $(shell id -u)

.PHONY: all check install create_user create_scripts install_plugins version count

all:
	# Type "make install" to install.

install: check_root install_curl install_git create_user install_python3 create_venv create_scripts create_configs patch_shebang install_plugins version

check:
	@command -v [ > /dev/null && echo "[ <expr> ] ... [OK]" || echo "[ <expr> ] ... [ERROR]"
	@command -v egrep > /dev/null && echo "egrep ... [OK]" || echo "egrep ... [ERROR]"
	@command -v useradd > /dev/null && echo "useradd ... [OK]" || echo "useradd ... [ERROR]"
	@command -v usermod > /dev/null && echo "usermod ... [OK]" || echo "usermod ... [ERROR]"
	@command -v gunzip > /dev/null && echo "gunzip ... [OK]" || echo "gunzip ... [ERROR]"
	@command -v apt-get > /dev/null && echo "apt-get ... [OK]" || echo "apt-get ... [ERROR]"
	@command -v curl > /dev/null && echo "curl ... [OK]" || echo "curl ... [ERROR]"
	@command -v git > /dev/null && echo "git ... [OK]" || echo "git ... [ERROR]"
	@command -v python3 > /dev/null && echo "python3 ... [OK]" || echo "python3 ... [ERROR]"
	@command -v easy_install3 > /dev/null && echo "easy_install3 ... [OK]" || echo "easy_install3 ... [ERROR]"
	@command -v pip3 > /dev/null && echo "pip3 ... [OK]" || echo "pip3 ... [ERROR]"
	@command -v virtualenv > /dev/null && echo "virtualenv ... [OK]" || echo "virtualenv ... [ERROR]"
	@command -v printenv > /dev/null && echo "printenv ... [OK]" || echo "printenv ... [ERROR]"
	@command -v dpkg > /dev/null && echo "dpkg ... [OK]" || echo "dpkg ... [ERROR]"

check_root:
	$(info CHECK ROOT USER)
	@[ $(CURRENT_USER_ID) = 0 ] || (echo '[ERROR] Required `root` user access (use: `sudo make install`)' && exit 31)

install_curl:
	$(info INSTALL CURL)
	@command -v curl > /dev/null || apt-get install curl -y

install_git:
	$(info INSTALL GIT)
	@command -v git > /dev/null || apt-get install git -y

install_python3:
	$(info INSTALL PYTHON3 EASY_INSTALL3 PIP3 VIRTUALENV)
	@command -v python3 > /dev/null || apt-get install python3-dev -y
	@command -v easy_install3 > /dev/null || apt-get install python3-setuptools -y
	@command -v pip3 > /dev/null || easy_install3 pip
	@command -v virtualenv > /dev/null || easy_install3 virtualenv

create_venv: install_python3
	$(info CREATE VENV ${PLATFORM_VENV_PATH})
	@[ -f ${PLATFORM_VENV_PATH}/bin/python ] || virtualenv --python=python3 --always-copy ${PLATFORM_VENV_PATH}
	@#[ -f ${PLATFORM_VENV_PATH}/requirements.txt ] || ${PLATFORM_VENV_PATH}/bin/pip install ./packages
	@[ -f ${PLATFORM_VENV_PATH}/requirements.txt ] || ${PLATFORM_VENV_PATH}/bin/pip install -e packages
	$(info WRITE INSTALLED PACKAGES ${PLATFORM_VENV_PATH}/requirements.txt)
	${PLATFORM_VENV_PATH}/bin/pip freeze > ${PLATFORM_VENV_PATH}/requirements.txt

create_user:
	$(info CREATE USER ${PLATFORM_USERNAME} HOME=${PLATFORM_DATA_PATH})
	@egrep -i "^${PLATFORM_USERNAME}" /etc/passwd > /dev/null || useradd --home-dir ${PLATFORM_DATA_PATH} --create-home --shell ${PLATFORM_PATH} ${PLATFORM_USERNAME}
	@git config --global user.email "${PLATFORM_USERNAME}@example.com" || echo "no git"
	@git config --global user.name "${PLATFORM_USERNAME}" || echo "no git"

create_scripts:
	$(info CREATE FILES)
	cp bin/${PLATFORM_NAME} ${PLATFORM_PATH}
	cp bin/${PLATFORM_PLUGIN_INSTALLER_COMMAND} ${PLATFORM_PLUGIN_INSTALLER_PATH}
	cp bin/${PLATFORM_PLUGIN_DEACTIVATOR_COMMAND} ${PLATFORM_PLUGIN_DEACTIVATOR_PATH}
	cp bin/${PLATFORM_PLUGIN_ACTIVATOR_COMMAND} ${PLATFORM_PLUGIN_ACTIVATOR_PATH}
	cp bin/${PLATFORM_TRIGGER_EVENT_COMMAND} ${PLATFORM_EVENT_TRIGGER_PATH}
	@chmod +x ${PLATFORM_PATH}
	@chmod +x ${PLATFORM_PLUGIN_INSTALLER_PATH}
	@chmod +x ${PLATFORM_PLUGIN_DEACTIVATOR_PATH}
	@chmod +x ${PLATFORM_PLUGIN_ACTIVATOR_PATH}
	@chmod +x ${PLATFORM_EVENT_TRIGGER_PATH}
	mkdir -p ${PLATFORM_PLUGINS_PATH}

create_configs:
	$(info CREATE CONFIG ${PLATFORM_PATH}.ini)
	@echo "$$CONFIG" > ${PLATFORM_PATH}.ini

patch_shebang:
	$(info PATCH SHEBANG ${PLATFORM_PATH})
	@sed -i "1 i\#!${PLATFORM_VENV_PATH}/bin/python3" ${PLATFORM_PATH}
	$(info PATCH SHEBANG ${PLATFORM_PLUGIN_INSTALLER_PATH})
	@sed -i "1 i\#!${PLATFORM_VENV_PATH}/bin/python3" ${PLATFORM_PLUGIN_INSTALLER_PATH}
	$(info PATCH SHEBANG ${PLATFORM_PLUGIN_DEACTIVATOR_PATH})
	@sed -i "1 i\#!${PLATFORM_VENV_PATH}/bin/python3" ${PLATFORM_PLUGIN_DEACTIVATOR_PATH}
	$(info PATCH SHEBANG ${PLATFORM_PLUGIN_ACTIVATOR_PATH})
	@sed -i "1 i\#!${PLATFORM_VENV_PATH}/bin/python3" ${PLATFORM_PLUGIN_ACTIVATOR_PATH}
	$(info PATCH SHEBANG ${PLATFORM_EVENT_TRIGGER_PATH})
	@sed -i "1 i\#!${PLATFORM_VENV_PATH}/bin/python3" ${PLATFORM_EVENT_TRIGGER_PATH}

install_plugins:
	$(info INSTALL PLUGINS from plugins/*)
	@${PLATFORM_PLUGIN_INSTALLER_PATH} plugins/* --force

version:
	$(info WRITE VERSION ${PLATFORM_DATA_PATH}/VERSION)
	@git describe --tags > ${PLATFORM_DATA_PATH}/VERSION  2> /dev/null || echo '~${PLATFORM_VERSION} ($(date -uIminutes))' > ${PLATFORM_DATA_PATH}/VERSION

count:
	@echo "core - `cat bin/${PLATFORM_NAME} | wc -l`"
	@echo "core-install-plugin - `cat bin/${PLATFORM_PLUGIN_INSTALLER_COMMAND} | wc -l`"
	@echo "core-trigger-event - `cat bin/${PLATFORM_TRIGGER_EVENT_COMMAND} | wc -l`"
	@echo "packages/ - `find packages -type f | grep -Ev '*.pyc' | xargs cat | wc -l` (test `find packages -type f | grep -Ev '*.pyc' | grep test/ | xargs cat | wc -l`)"
	@echo "test.py - `cat test.py | wc -l`"
	@echo "plugins/ - `find plugins -type f | xargs cat | wc -l`"
	@echo "tests/ - `find tests -type f | xargs cat | wc -l`"

clean: check_root
	$(info CLEAN ${PLATFORM_PLUGINS_PATH} ${PLATFORM_VENV_PATH} ${PLATFORM_PATH} ${PLATFORM_PLUGIN_INSTALLER_PATH})
	rm -rf ${PLATFORM_PLUGINS_PATH}
	rm -rf ${PLATFORM_VENV_PATH}
	rm -f ${PLATFORM_PATH} ${PLATFORM_PATH}.ini
	rm -f ${PLATFORM_PLUGIN_INSTALLER_PATH} ${PLATFORM_PLUGIN_INSTALLER_PATH}.ini
	rm -f ${PLATFORM_EVENT_TRIGGER_PATH} ${PLATFORM_EVENT_TRIGGER_PATH}.ini

full_clean: check_root clean
	$(info CLEAN USER ${PLATFORM_USERNAME} AND DATA ${PLATFORM_DATA_PATH})
	rm -rf ${PLATFORM_DATA_PATH}
	userdel ${PLATFORM_USERNAME} || echo "user '${PLATFORM_USERNAME}' not exists"

reinstall: full_clean install
	@echo "done"

install_test_pythons: check_root
	add-apt-repository ppa:fkrull/deadsnakes -y
	apt-get update
	apt-get install python2.7 python3.2 python3.4 -y
	# TODO: check 'dpkg -s python3.4 > /dev/null' for speed up

test_requirements:
	pip3 install -r test_requirements.txt

test: check_root install_test_pythons test_requirements
	find . -name "*.pyc" -exec rm -rf {} \;
	tox
	python3 test.py

fast_test:
	find . -name "*.pyc" -exec rm -rf {} \;
	py.test --showlocals --debug --cov-config .coveragerc --cov packages --durations=10 packages/
	python3 test.py

retest: full_clean install test
	@echo "done"

active:
	@echo . "$(PLATFORM_VENV_PATH)/bin/activate" # use `make active` for activate venv

activate: active

clean_docker:
	# Delete all containers
	docker rm -f $$(docker ps -a -q) || echo "no containers"
	# Delete all images
	docker rmi $$(docker images | grep build__ |awk '{print($$3)}')

# cd /vagrant && make create_scripts patch_shebang && cd - && wflow-install-plugin /vagrant/plugins/* --force && git push ssh://wflow@127.0.0.1/test4 master
