# Database Migrations

This directory contains scripts to set up and populate the database with initial data.

## Available Scripts

- `run_migrations.py`: Main Python script to run all migrations
- `run_migrations.sh`: Shell script for Unix/Linux/Mac users
- `run_migrations.bat`: Batch script for Windows users
- `create_admin.py`: Creates an admin user
- `populate_buses.py`: Populates the database with sample bus data

## Usage

### Using Shell Scripts (Recommended)

#### Unix/Linux/Mac:

```bash
# Make the script executable
chmod +x run_migrations.sh

# Run all migrations
./run_migrations.sh

# Show help
./run_migrations.sh --help

# Run specific migrations
./run_migrations.sh --admin-only
./run_migrations.sh --buses-only

# Create custom admin user
./run_migrations.sh --admin johndoe john@example.com password123
```

#### Windows:

```cmd
# Run all migrations
run_migrations.bat

# Show help
run_migrations.bat --help

# Run specific migrations
run_migrations.bat --admin-only
run_migrations.bat --buses-only

# Create custom admin user
run_migrations.bat --admin johndoe john@example.com password123
```

### Using Python Directly

```bash
# Run all migrations
python run_migrations.py

# Run specific migrations
python run_migrations.py --admin-only
python run_migrations.py --buses-only

# Create custom admin user
python run_migrations.py --admin-username "yourusername" --admin-email "your@email.com" --admin-password "yourpassword"
```

### Run Individual Scripts

```bash
# Create default admin user
python create_admin.py

# Create custom admin user
python create_admin.py username email password

# Populate buses
python populate_buses.py
```

## Default Admin Credentials

- Username: admin
- Email: admin@example.com
- Password: admin123

**Note:** It's recommended to change these default credentials in a production environment. 