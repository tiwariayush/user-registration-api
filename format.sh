#!/bin/bash

echo "Formatting code..."

echo "Running Black..."
black . --exclude="/(pyproject\.toml|\.flake8|lint\.sh|format\.sh)/"

echo "Sorting imports..."
isort . --skip-glob="*.toml" --skip-glob="*.sh" --skip-glob="*.flake8"

echo "Done."
