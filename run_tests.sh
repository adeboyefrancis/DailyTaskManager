#!/bin/bash
# Daily Task Manager - Test Runner Script
# Runs all tests with coverage reporting

set -e

echo "================================"
echo "Daily Task Manager - Test Suite"
echo "================================"
echo ""

# Check if pytest is installed
if ! python3 -m pytest --version &> /dev/null; then
    echo "❌ pytest is not installed. Installing dependencies..."
    python3 -m pip install -r requirements.txt
    echo ""
fi

# Run tests with coverage
echo "🧪 Running all tests..."
echo ""

# Set PYTHONPATH to include project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run tests with coverage
python3 -m pytest -vv --cov=backend backend/tests/

echo ""
echo "✅ All tests passed!"
