#!/usr/bin/env bash

# determine if we are on XF OS or not
if test -d "/opt/App/.venv3.8"; then
    py_ex="/opt/App/.venv3.8/bin/python3.8"
elif test -d "/opt/App/.venv3.11"; then
    py_ex="/opt/App/.venv3.11/bin/python3.11"
else
    py_ex="/usr/bin/python3.6"
fi

# we must kill btp as Kivy is a bit borg-ish about multiple windows
# we kill everything
pkill -f $py_ex

cd /usr/local/share/btkivy

$py_ex main.py
