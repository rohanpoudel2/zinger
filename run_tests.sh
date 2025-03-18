#!/bin/bash

# Exit on any error
set -e

# Create and activate virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python -m venv venv
    echo -e "${GREEN}Virtual environment created!${NC}"
fi

# Activate the virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source venv/Scripts/activate
else
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source venv/bin/activate
fi

# Install requirements
echo -e "${YELLOW}Installing requirements...${NC}"
pip install -r requirements.txt

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
