#!/usr/bin/env bash
set -eo pipefail
export DEBIAN_FRONTEND=noninteractive
export REPO="https://github.com/pahaz/wflow.git"
export BRANCH=master

command -v apt-get > /dev/null || (echo "This installation script requires apt-get." && exit 1)

apt-get update
apt-get install make git -y

cd /tmp/ && test -d .build || git clone $REPO .build
cd .build

#git fetch origin
#if [[ -n $BRANCH ]]; then
#  git checkout origin/$BRANCH
#elif [[ -n $TAG ]]; then
#  git checkout $TAG
#fi

make install

echo "INSTALLED PLUGINS IS:"
wflow-install-plugin -l

echo
echo "Almost done! Now use 'wflow', 'wflow-install-plugin' "
echo "and 'wflow-trigger-event'"
