#!/bin/bash
# Shell script to run database migrations from the root directory

# Set the migrations directory path
MIGRATIONS_DIR="src/migrations"

# Set PYTHONPATH to include src directory
export PYTHONPATH=src:$PYTHONPATH

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Display help message
show_help() {
    echo "Bus Booking System - Database Migration Script"
    echo ""
    echo "Usage: ./run_migrations.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --help                 Show this help message"
    echo "  --all                  Run all migrations (default)"
    echo "  --reset-only           Only reset the database schema"
    echo "  --buses-only           Only populate bus data"
    echo "  --admin-only           Only create default admin user"
    echo "  --admin USERNAME EMAIL PASSWORD  Create custom admin user"
    echo ""
    echo "Examples:"
    echo "  ./run_migrations.sh --all"
    echo "  ./run_migrations.sh --reset-only"
    echo "  ./run_migrations.sh --buses-only"
    echo "  ./run_migrations.sh --admin johndoe john@example.com password123"
    echo ""
}

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "Error: Python is not installed or not in PATH"
    exit 1
fi

# Check if migrations directory exists
if [ ! -d "$MIGRATIONS_DIR" ]; then
    echo "Error: Migrations directory not found at $MIGRATIONS_DIR"
    exit 1
fi

run_all_migrations() {
    echo "1. Resetting database schema..."
    python "$MIGRATIONS_DIR/reset_database.py" || exit 1
    
    echo "2. Populating bus data..."
    python "$MIGRATIONS_DIR/populate_buses.py" || exit 1
    
    echo "3. Creating default admin user..."
    python "$MIGRATIONS_DIR/create_admin.py" || exit 1
}

# Default option is to run all migrations
if [ $# -eq 0 ]; then
    run_all_migrations
    exit 0
fi

# Parse command line arguments
case "$1" in
    --help)
        show_help
        exit 0
        ;;
    --all)
        run_all_migrations
        ;;
    --reset-only)
        echo "Resetting database schema only..."
        python "$MIGRATIONS_DIR/reset_database.py"
        ;;
    --buses-only)
        echo "Populating bus data only..."
        python "$MIGRATIONS_DIR/populate_buses.py"
        ;;
    --admin-only)
        echo "Creating default admin user only..."
        python "$MIGRATIONS_DIR/create_admin.py"
        ;;
    --admin)
        if [ $# -ne 4 ]; then
            echo "Error: --admin option requires username, email, and password"
            echo "Usage: ./run_migrations.sh --admin USERNAME EMAIL PASSWORD"
            exit 1
        fi
        echo "Creating custom admin user..."
        USERNAME="$2" EMAIL="$3" PASSWORD="$4" python "$MIGRATIONS_DIR/create_admin.py"
        ;;
    *)
        echo "Error: Unknown option '$1'"
        show_help
        exit 1
        ;;
esac

echo "Migration completed successfully!" 