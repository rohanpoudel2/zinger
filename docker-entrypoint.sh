#!/bin/bash

# Make the migration script executable
chmod +x /app/run_migrations.sh

# If the first argument is "migrate"
if [ "$1" = "migrate" ]; then
    # If no additional arguments, run all migrations
    if [ "$#" -eq 1 ]; then
        ./run_migrations.sh
    else
        # Pass all remaining arguments to the migration script
        shift
        ./run_migrations.sh "$@"
    fi
elif [ "$1" = "start" ]; then
    # Run the application
    python src/main.py
else
    # Show usage
    echo "Usage:"
    echo "  migrate [OPTIONS]  - Run database migrations"
    echo "  start            - Start the application"
    echo ""
    echo "Migration options:"
    echo "  --all                  Run all migrations (default)"
    echo "  --admin-only           Run only admin user migration"
    echo "  --buses-only           Run only bus data migration"
    echo "  --admin USERNAME EMAIL PASSWORD  Create custom admin user"
    exit 1
fi 