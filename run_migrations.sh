#!/bin/bash
# Shell script to run database migrations from the root directory

# Set the migrations directory path
MIGRATIONS_DIR="src/migrations"

# Display help message
show_help() {
    echo "Bus Booking System - Database Migration Script"
    echo ""
    echo "Usage: ./run_migrations.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --help                 Show this help message"
    echo "  --all                  Run all migrations (default)"
    echo "  --admin-only           Run only admin user migration"
    echo "  --buses-only           Run only bus data migration"
    echo "  --admin USERNAME EMAIL PASSWORD  Create custom admin user"
    echo ""
    echo "Examples:"
    echo "  ./run_migrations.sh --all"
    echo "  ./run_migrations.sh --admin-only"
    echo "  ./run_migrations.sh --buses-only"
    echo "  ./run_migrations.sh --admin johndoe john@example.com password123"
    echo ""
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    # Try with just 'python' if python3 is not found
    if ! command -v python &> /dev/null; then
        echo "Error: Python is not installed or not in PATH"
        exit 1
    fi
    PYTHON_CMD="python"
else
    PYTHON_CMD="python3"
fi

# Check if migrations directory exists
if [ ! -d "$MIGRATIONS_DIR" ]; then
    echo "Error: Migrations directory not found at $MIGRATIONS_DIR"
    exit 1
fi

# Default option is to run all migrations
if [ $# -eq 0 ]; then
    echo "Running all migrations..."
    $PYTHON_CMD $MIGRATIONS_DIR/run_migrations.py
    exit 0
fi

# Parse command line arguments
case "$1" in
    --help)
        show_help
        exit 0
        ;;
    --all)
        echo "Running all migrations..."
        $PYTHON_CMD $MIGRATIONS_DIR/run_migrations.py
        ;;
    --admin-only)
        echo "Running admin user migration only..."
        $PYTHON_CMD $MIGRATIONS_DIR/run_migrations.py --admin-only
        ;;
    --buses-only)
        echo "Running bus data migration only..."
        $PYTHON_CMD $MIGRATIONS_DIR/run_migrations.py --buses-only
        ;;
    --admin)
        if [ $# -ne 4 ]; then
            echo "Error: --admin option requires username, email, and password"
            echo "Usage: ./run_migrations.sh --admin USERNAME EMAIL PASSWORD"
            exit 1
        fi
        echo "Creating custom admin user..."
        $PYTHON_CMD $MIGRATIONS_DIR/run_migrations.py --admin-username "$2" --admin-email "$3" --admin-password "$4"
        ;;
    *)
        echo "Error: Unknown option '$1'"
        show_help
        exit 1
        ;;
esac

echo "Migration completed successfully!" 