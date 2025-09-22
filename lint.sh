#!/bin/bash

echo "Running code quality checks..."

echo "Checking code formatting..."
black --check --diff . --exclude="/(pyproject\.toml|\.flake8|lint\.sh|format\.sh)/"
BLACK_EXIT=$?

echo "Checking import sorting..."
isort --check-only --diff . --skip-glob="*.toml" --skip-glob="*.sh" --skip-glob="*.flake8"
ISORT_EXIT=$?

echo "Running style checks..."
flake8 . --exclude="*.toml,*.sh"
FLAKE8_EXIT=$?

echo "Running type checks..."
mypy . --ignore-missing-imports --exclude="(pyproject\.toml|\.flake8|lint\.sh|format\.sh)"
MYPY_EXIT=$?

echo ""
echo "Summary:"
echo "--------"
echo "Black:   $([ $BLACK_EXIT -eq 0 ] && echo "PASS" || echo "FAIL")"
echo "isort:   $([ $ISORT_EXIT -eq 0 ] && echo "PASS" || echo "FAIL")"  
echo "Flake8:  $([ $FLAKE8_EXIT -eq 0 ] && echo "PASS" || echo "FAIL")"
echo "MyPy:    $([ $MYPY_EXIT -eq 0 ] && echo "PASS" || echo "FAIL")"

if [ $BLACK_EXIT -ne 0 ] || [ $ISORT_EXIT -ne 0 ] || [ $FLAKE8_EXIT -ne 0 ] || [ $MYPY_EXIT -ne 0 ]; then
    echo ""
    echo "Linting failed. Please fix the issues above."
    exit 1
else
    echo ""
    echo "All checks passed."
    exit 0
fi
