#!/bin/sh
# Existing Claude Code entry point; the product's shared Skill linker owns it.
set -eu
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
exec "$script_dir/link-skills.sh" claude "$@"
