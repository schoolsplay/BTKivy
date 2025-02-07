#!/usr/bin/env bash
export DEBUG='1'

if [[ -z "${VIRTUAL_ENV}" ]]; then
        echo "No virtual environment is set!!!!"
        echo "quiting"
        exit 1
fi

python3 main.py


