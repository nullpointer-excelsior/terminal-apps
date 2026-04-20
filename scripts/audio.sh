#!/bin/bash

TARGET_DIR="$HOME/Repositories/terminal-apps"
PYTHONPATH="$TARGET_DIR" "$TARGET_DIR/.venv/bin/python" -m audio "$@"
