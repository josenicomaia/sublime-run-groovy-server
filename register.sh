#!/bin/bash
ln -sf $(dirname $(readlink -f "$0"))"/run_groovy_server.py" ~/.config/sublime-text-3/Packages/User/expand_to_paragraph.py
