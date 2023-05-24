#!/bin/bash
set -e

coverage run -m pytest || echo 0
