#!/bin/bash
DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

dest=${1-./venv}

python3 -m venv ${dest}
source ${dest}/bin/activate

pushd ${DIR} > /dev/null

pip install wheel
pip install pytest
pip install pytest-cov
pip install pytest-mock
pip install -r requirements.txt
pip install -e .

popd > /dev/null
