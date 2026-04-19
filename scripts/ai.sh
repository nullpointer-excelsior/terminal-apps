#!/bin/bash

TARGET_DIR="$HOME/Repositories/terminal-apps"
cd "$TARGET_DIR" && uv run -m ai "$@"

