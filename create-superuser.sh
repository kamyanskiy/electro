#!/bin/bash
# Script to create a superuser for Electro Management System

cd "$(dirname "$0")/backend" || exit 1

python cli.py create-superuser "$@"
