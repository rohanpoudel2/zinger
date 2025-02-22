#!/bin/bash

# Navigate to the project directory
cd "$(dirname "$0")"

# Ensure that the Python virtual environment is activated (optional)
# If you're using a virtual environment, uncomment the following line and adjust the path if necessary:
# source venv/bin/activate

# Run the tests
echo "Running tests..."

# Running all the tests in the 'tests' directory
python3 -m unittest discover -s tests -p "*.py" || { echo "Some tests failed."; exit 1; }

echo "All tests passed!"
