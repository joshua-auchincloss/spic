#!/bin/bash

coverage combine
coverage report --show-missing --format=markdown > COVERAGE.md
