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

4. Docker Build the Image:
   ```bash
   docker build -t zinger .
   ```

5. Docker run all the migration:
   ```bash
   docker run -it zinger migrate
   ```
   
   You can also run specific migrations with flags:
   ```bash
   docker run -it zinger migrate --admin-only
   docker run -it zinger migrate --buses-only
   docker run -it zinger migrate --admin USERNAME EMAIL PASSWORD
   ```

6. Docker Run the application:
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

### Test Structure

Tests are organized by component:

- `test_booking_repository.py` - Tests for the BookingRepository class
- `test_booking_service.py` - Tests for the BookingService class
- `test_bus_repository.py` - Tests for the BusRepository class
- `test_user_repository.py` - Tests for the UserRepository class
- `test_auth_service.py` - Tests for the AuthService class
- `test_transit_service.py` - Tests for the TransitService class
- `test_location_service.py` - Tests for the LocationService class

### Creating New Tests

When adding new functionality, create or update the corresponding test files. Test files should be placed in the `src/tests` directory and follow the naming convention `test_*.py`.

Each test file should:
1. Import the necessary modules and classes
2. Create a test class that extends `unittest.TestCase`
3. Implement test methods following the naming convention `test_*`
4. Use assertions to verify expected behavior
5. Include proper setup and teardown methods if needed

Example:

```python
import unittest
from unittest.mock import MagicMock

class TestMyComponent(unittest.TestCase):
    def setUp(self):
        # Setup code runs before each test
        pass
        
    def test_my_method(self):
        # Test specific functionality
        self.assertEqual(2 + 2, 4)
        
    def tearDown(self):
        # Cleanup code runs after each test
        pass
```

### Test Database

Tests use an in-memory SQLite database to avoid affecting the production database. This ensures tests are isolated and can run independently without side effects.
