#!/bin/bash

D=$(pwd)
SCRIPT_DIR=$(dirname $0)
cd $SCRIPT_DIR


run_python() {
    python -m robota "$@"
}

export -f run_python

poetry run bash -c 'cd $D && run_python "$0" "$@"' -- "$@"
