#!/bin/bash
DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

pushd ${DIR} > /dev/null

pylint src/

popd > /dev/null
