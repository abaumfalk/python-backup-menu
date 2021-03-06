#!/bin/bash
set -e
DIR=$(cd `dirname $0` && pwd)

if [ ! -e "${DIR}/venv" ]; then
    ./python-backup-menu/make_virtualenv.sh "${DIR}/venv"
fi

source "${DIR}/venv/bin/activate"

backup -c "${DIR}/config.py"
