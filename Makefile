# settings begin

SCRIPT_VERSION = master

SCRIPT_NAME ?= wflow
SCRIPT_PLUGIN_INSTALLER_NAME ?= ${SCRIPT_NAME}-install-plugin
SCRIPT_TRIGGER_EVENT_NAME ?= ${SCRIPT_NAME}-trigger-event

SCRIPT_USER_NAME ?= wflow
SCRIPT_DATA_PATH ?= /home/${SCRIPT_USER_NAME}

SCRIPT_PLUGIN_PATH ?= /var/lib/${SCRIPT_NAME}/plugins
SCRIPT_VENV_PATH ?= /var/lib/${SCRIPT_NAME}/venv
SCRIPT_PATH ?= /usr/local/bin/${SCRIPT_NAME}
SCRIPT_PLUGIN_INSTALLER_PATH ?= /usr/local/bin/${SCRIPT_PLUGIN_INSTALLER_NAME}
SCRIPT_TRIGGER_EVENT_PATH ?= /usr/local/bin/${SCRIPT_TRIGGER_EVENT_NAME}

# settings end

define CONFIG
[DEFAULT]
SCRIPT_NAME = ${SCRIPT_NAME}
SCRIPT_PATH = ${SCRIPT_PATH}
SCRIPT_PLUGIN_INSTALLER_NAME = ${SCRIPT_PLUGIN_INSTALLER_NAME}
SCRIPT_PLUGIN_INSTALLER_PATH = ${SCRIPT_PLUGIN_INSTALLER_PATH}
SCRIPT_TRIGGER_EVENT_NAME = ${SCRIPT_TRIGGER_EVENT_NAME}
SCRIPT_TRIGGER_EVENT_PATH = ${SCRIPT_TRIGGER_EVENT_PATH}
SCRIPT_PLUGIN_PATH = ${SCRIPT_PLUGIN_PATH}
SCRIPT_VENV_PATH = ${SCRIPT_VENV_PATH}
SCRIPT_USER_NAME = ${SCRIPT_USER_NAME}
SCRIPT_DATA_PATH = ${SCRIPT_DATA_PATH}
endef

export CONFIG

CURRENT_USER_ID = $(shell id -u)

.PHONY: all check install create_user create_files install_plugins version count

all:
	# Type "make install" to install.

install: check_root install_curl install_python3 install_git create_user create_files create_configs patch_shebang install_plugins version

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

check_root:
	$(info CHECK ROOT USER)
	@[ $(CURRENT_USER_ID) = 0 ] || (echo '[ERROR] Required `root` user access (use: `sudo make install`)' && exit 31)

install_curl:
	$(info INSTALL CURL)
	@command -v curl > /dev/null || apt-get install curl -y

install_python3:
	$(info INSTALL PYTHON3 EASY_INSTALL3 PIP3 VIRTUALENV)
	@command -v python3 > /dev/null || apt-get install python3-dev -y
	@command -v easy_install3 > /dev/null || apt-get install python3-setuptools -y
	@command -v pip3 > /dev/null || easy_install3 pip
	@command -v virtualenv > /dev/null || easy_install3 virtualenv

install_git:
	$(info INSTALL GIT)
	@command -v git > /dev/null || apt-get install git -y

create_venv: install_python3
	$(info CREATE VENV ${SCRIPT_VENV_PATH})
	@[ -f ${SCRIPT_VENV_PATH}/bin/python ] || virtualenv --python=python3 --always-copy ${SCRIPT_VENV_PATH}
	@[ -f ${SCRIPT_VENV_PATH}/requirements.txt ] || ${SCRIPT_VENV_PATH}/bin/pip install -e packages
	$(info WRITE INSTALLED PACKAGES ${SCRIPT_VENV_PATH}/requirements.txt)
	${SCRIPT_VENV_PATH}/bin/pip freeze > ${SCRIPT_VENV_PATH}/requirements.txt

create_user: install_git
	$(info CREATE USER ${SCRIPT_USER_NAME} HOME=${SCRIPT_DATA_PATH})
	@egrep -i "^${SCRIPT_USER_NAME}" /etc/passwd > /dev/null || useradd --home-dir ${SCRIPT_DATA_PATH} --create-home --shell ${SCRIPT_PATH} ${SCRIPT_USER_NAME}
	@git config --global user.email "${SCRIPT_USER_NAME}@example.com"
	@git config --global user.name "${SCRIPT_USER_NAME}"

create_files: create_venv
	$(info CREATE FILES)
	cp ${SCRIPT_NAME} ${SCRIPT_PATH}
	cp ${SCRIPT_PLUGIN_INSTALLER_NAME} ${SCRIPT_PLUGIN_INSTALLER_PATH}
	cp ${SCRIPT_TRIGGER_EVENT_NAME} ${SCRIPT_TRIGGER_EVENT_PATH}
	@chmod +x ${SCRIPT_PATH}
	@chmod +x ${SCRIPT_PLUGIN_INSTALLER_PATH}
	@chmod +x ${SCRIPT_TRIGGER_EVENT_PATH}
	mkdir -p ${SCRIPT_PLUGIN_PATH}

create_configs: create_files
	$(info CREATE CONFIG ${SCRIPT_PATH}.ini AND SYMLINK ${SCRIPT_PLUGIN_INSTALLER_PATH}.ini)
	@echo "$$CONFIG" > ${SCRIPT_PATH}.ini
	ln -sf ${SCRIPT_PATH}.ini ${SCRIPT_PLUGIN_INSTALLER_PATH}.ini
	ln -sf ${SCRIPT_PATH}.ini ${SCRIPT_TRIGGER_EVENT_PATH}.ini

patch_shebang: create_venv
	$(info PATCH SHEBANG ${SCRIPT_PATH})
	@sed -i "1 i\#!${SCRIPT_VENV_PATH}/bin/python3" ${SCRIPT_PATH}
	$(info PATCH SHEBANG ${SCRIPT_PLUGIN_INSTALLER_PATH})
	@sed -i "1 i\#!${SCRIPT_VENV_PATH}/bin/python3" ${SCRIPT_PLUGIN_INSTALLER_PATH}
	$(info PATCH SHEBANG ${SCRIPT_TRIGGER_EVENT_PATH})
	@sed -i "1 i\#!${SCRIPT_VENV_PATH}/bin/python3" ${SCRIPT_TRIGGER_EVENT_PATH}

install_plugins: create_venv create_files create_configs patch_shebang
	$(info INSTALL PLUGINS from plugins/*)
	@${SCRIPT_PLUGIN_INSTALLER_PATH} plugins/*

version: install_git
	$(info WRITE VERSION ${SCRIPT_DATA_PATH}/VERSION)
	@git describe --tags > ${SCRIPT_DATA_PATH}/VERSION  2> /dev/null || echo '~${SCRIPT_VERSION} ($(date -uIminutes))' > ${SCRIPT_DATA_PATH}/VERSION

count:
	@echo "Core lines:"
	@cat ${SCRIPT_NAME} | wc -l
	@echo "Plugin installer lines:"
	@cat ${SCRIPT_PLUGIN_INSTALLER_NAME} | wc -l
	@echo "Event trigger lines:"
	@cat ${SCRIPT_TRIGGER_EVENT_NAME} | wc -l
	@echo "Plugin lines:"
	@find plugins -type f | xargs cat | wc -l
	@echo "Packages lines:"
	@find packages -type f | xargs cat | wc -l
	@echo "Test lines:"
	@find tests -type f | xargs cat | wc -l

clean: check_root
	$(info CLEAN ${SCRIPT_PLUGIN_PATH} ${SCRIPT_VENV_PATH} ${SCRIPT_PATH} ${SCRIPT_PLUGIN_INSTALLER_PATH})
	rm -rf ${SCRIPT_PLUGIN_PATH}
	rm -rf ${SCRIPT_VENV_PATH}
	rm -f ${SCRIPT_PATH} ${SCRIPT_PATH}.ini
	rm -f ${SCRIPT_PLUGIN_INSTALLER_PATH} ${SCRIPT_PLUGIN_INSTALLER_PATH}.ini
	rm -f ${SCRIPT_TRIGGER_EVENT_PATH} ${SCRIPT_TRIGGER_EVENT_PATH}.ini

full_clean: check_root clean
	$(info CLEAN USER ${SCRIPT_USER_NAME} AND DATA ${SCRIPT_DATA_PATH})
	rm -rf ${SCRIPT_DATA_PATH}
	userdel ${SCRIPT_USER_NAME}
