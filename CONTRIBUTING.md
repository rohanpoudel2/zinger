# Contributing to Bus Tracking System - Sprint 1

## Current Implementation
We have implemented the basic structure with:
- Interactive CLI menu
- In-memory storage system
- Basic booking and cancellation functionality
- Simple bus tracking simulation

## Sprint 1 Tasks

### 1. Model Implementation
Convert the current dictionary-based storage to proper OOP models:

```python
# src/models/bus.py
class Bus:
    def __init__(self, bus_number: str, route: str, departure: str, total_seats: int, fare: float):
        # Convert current dictionary structure to proper OOP
        # Add seat management methods
        pass

# src/models/ticket.py
class Ticket:
    def __init__(self, booking_id: str, bus: Bus, passenger_name: str, seat: str):
        # Convert booking dictionary to proper ticket class
        # Add basic status management (Confirmed/Cancelled)
        pass

# src/models/user.py
class User:
    def __init__(self, name: str, role: str = "passenger"):
        # Basic user properties
        # Simple role-based authorization (passenger/staff)
        pass
```

### 2. Feature Enhancements

#### Booking System
- [ ] Implement seat validation in Bus class
- [ ] Add booking confirmation details
- [ ] Implement basic error handling for invalid inputs
- [ ] Add simple booking receipt generation

#### User Management
- [ ] Add basic user roles (passenger/staff)
- [ ] Implement role-based menu options
- [ ] Add user session management (current user context)

#### Bus Management
- [ ] Add bus schedule validation
- [ ] Implement seat layout visualization
- [ ] Add basic route information

### 3. Testing
- [ ] Add basic unit tests for models
- [ ] Test booking flow
- [ ] Test seat management
- [ ] Test role-based access

## How to Get Started
1. Pick an unassigned task
2. Create a new branch: `git checkout -b feature/your-feature-name`
3. Implement your changes
4. Test your implementation
5. Create a pull request

## Code Style Guidelines
- Follow PEP 8 standards
- Add docstrings to classes and methods
- Include type hints
- Write meaningful commit messages

## Current Files Structure
```
bus_reservation/
├── src/
│   ├── models/
│   │   ├── bus.py      # Convert to OOP
│   │   ├── ticket.py   # Convert to OOP
│   │   └── user.py     # Add basic roles
│   ├── utils/
│   │   ├── logger.py   # Logging implementation
│   │   └── storage.py  # Current in-memory storage
│   └── main.py         # CLI interface
├── run.sh              # Run script
└── requirements.txt    # Project dependencies
```

## Task Distribution Suggestion
1. **Team Member 1**: Bus model and seat management
2. **Team Member 2**: Ticket model and booking flow
3. **Team Member 3**: User model and role-based access
4. **Team Member 4**: Testing and bug fixes

## Definition of Done
- Code follows OOP principles
- Basic error handling is implemented
- Code is tested
- Code follows style guidelines
- Pull request is reviewed by at least one team member 