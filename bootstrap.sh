#!/usr/bin/env bash
set -eo pipefail
export DEBIAN_FRONTEND=noninteractive
export REPO="https://github.com/8iq/wflow-core.git"
export BRANCH=master

command -v apt-get > /dev/null || (echo "This installation script requires apt-get." && exit 1)

#apt-get update
#apt-get install make git -y

make install

echo
echo "Almost done! Now use `wflow --help` and `wflow-install-plugin --help`"
