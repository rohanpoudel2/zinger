# Bus Tracking System

A command-line interface (CLI) application for bus ticket booking and tracking system.

## Project Overview

This project is developed as part of CSCI 6651 course at University of New Haven. The system allows passengers to book tickets, check bus availability, and track real-time bus locations.

## Features (Sprint 1)

- Command-line interface (CLI) for basic operations
- User authentication and management
- Bus information management
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

## Team Members

- Aryan Tandon
- Ashish Khadka
- Nipson KC
- Rohan Poudel
