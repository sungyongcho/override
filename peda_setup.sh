#!/bin/bash

## peda
## a plugin works with gdb
# https://github.com/longld/peda

# either this script, or the commands below needs to be executed on each level
chmod +rwx ~
echo "source /tmp/peda/peda.py" >> ~/.gdbinit
