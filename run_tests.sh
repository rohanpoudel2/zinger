#!/bin/bash

# Exit on any error
set -e

# Navigate to the project directory
cd "$(dirname "$0")"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting test suite...${NC}\n"

# Add src directory to PYTHONPATH to allow imports
export PYTHONPATH=$PYTHONPATH:$(pwd)/src

# Run the tests
echo -e "${BLUE}Running tests...${NC}"
python3 -m unittest discover -s src/tests -p "test_*.py" -v || {
    echo -e "\n${RED}Tests failed!${NC}"
    exit 1
}

echo -e "\n${GREEN}All tests passed successfully!${NC}"
