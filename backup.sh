#!/bin/bash
set -e
DIR=$(realpath "$(dirname "$(readlink "${BASH_SOURCE[0]}")")")

if [ ! -e "${DIR}/venv" ]; then
    "${DIR}/make_virtualenv.sh" "${DIR}/venv"
fi

source "${DIR}/venv/bin/activate"

backup -c config.py "$@"
