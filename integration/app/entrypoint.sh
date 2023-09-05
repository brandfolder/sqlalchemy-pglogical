#!/usr/bin/env bash

if [[ $# -gt 0 ]]; then
    exec bash -c "$@"
else
    exec sleep 3600
fi