# Team Zinger

A command-line interface (CLI) application for bus ticket booking and tracking system.

## Project Overview

This project is developed as part of CSCI 6651 course at University of New Haven. The system allows passengers to book tickets, check bus availability, and track real-time bus locations.
## Features (Sprint 1)

- Command-line interface (CLI) for basic operations
- Bus information
- Ticket booking and cancellation
- Basic in-memory storage system
- Error handling and logging

## Features (Sprint 2)

- Integrated SQLite for a database system.
- Implemented current user location.
- Added authentication and authorization.
- Fetched and displayed transit data from CTTransit API.
- Mapping Routes name and ID with caching.
- Limiting the bus data to 3 miles radius of the user. 
- Use threading to update routes periodically.
- Separate Admin Dashmenu options.
- Export booking data to a csv file.
- Using ORM for database operations. 
- Mesmerizing CLI interface using colors and tables.
- Updated project structure 
- Logging


## Setup & Running the Application

### Option 1: Using run.sh (Recommended)

1. Make the run script executable:
   ```bash
   chmod +x run.sh
   ```

2. Run the application:
   ```bash
   ./run.sh
   ```

The run script will automatically:
- Create a virtual environment if it doesn't exist
- Install required dependencies
- Start the application

### Option 2: Manual Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python -m src.main
   ```

### Option 3: Docker

1. Docker Build the Image:
   ```bash
   docker build -t zinger .
   ```

2. Docker run all the migration:
   ```bash
   docker run -it zinger migrate
   ```
   
   You can also run specific migrations with flags:
   ```bash
   docker run -it zinger migrate --admin-only
   docker run -it zinger migrate --buses-only
   docker run -it zinger migrate --admin USERNAME EMAIL PASSWORD
   ```

3. Docker Run the application:
   ```bash
   docker run -it zinger start
   ```

## Team Members

- Aryan Tandon
- Ashish Khadka
- Nipson KC
- Rohan Poudel

## Testing

The project includes comprehensive unit tests for all components. These tests focus on testing individual methods rather than through the UI.

### Running Tests

You can run all tests with the provided script:

```bash
chmod +x run_tests.sh
./run_tests.sh
```

This will run all test cases and show a summary of the results.