#!/usr/bin/env bash

# Get the directory of this file
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

ansible-playbook $DIR/setup/setup.yaml
