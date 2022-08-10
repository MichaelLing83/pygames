#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR

virtualenv -p python3 .venv
source .venv/bin/activate
pip3 install -r requirements.txt