#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Bus Reservation System ===${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}Virtual environment created!${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install requirements
echo -e "${YELLOW}Installing requirements...${NC}"
pip install -r requirements.txt > /dev/null 2>&1

# Run the application
echo -e "${GREEN}Starting the application...${NC}"
python src/main.py

# Deactivate virtual environment
deactivate 