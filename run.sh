#!/bin/bash

D=$(pwd)

SCRIPT_DIR=$(dirname $0)
cd $SCRIPT_DIR


ROBOTA_CODE_DIR="$D" poetry run python -m robota "$@"
