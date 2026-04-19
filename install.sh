#!/bin/bash

# installation directory
INSTALLATION_DIR="$HOME/.scripts"

# copy scripts
for script_path in scripts/*.sh; do
    script_name=$(basename "$script_path")
    name_without_ext="${script_name%.sh}"
    cp "$script_path" "$INSTALLATION_DIR/$name_without_ext"
done

