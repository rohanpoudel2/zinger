import sys
import os
import argparse

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from migrations.create_admin import create_admin_user
from migrations.populate_buses import populate_buses

def run_migrations(admin_only=False, buses_only=False):
    """Run all migrations."""
    print("Running database migrations...")
    
    if not admin_only and not buses_only:
        # Run all migrations
        create_admin_user()
        populate_buses()
    elif admin_only:
        # Run only admin user migration
        create_admin_user()
    elif buses_only:
        # Run only bus data migration
        populate_buses()
    
    print("Migrations completed successfully.")

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run database migrations")
    parser.add_argument("--admin-only", action="store_true", help="Run only admin user migration")
    parser.add_argument("--buses-only", action="store_true", help="Run only bus data migration")
    parser.add_argument("--admin-username", help="Admin username")
    parser.add_argument("--admin-email", help="Admin email")
    parser.add_argument("--admin-password", help="Admin password")
    
    args = parser.parse_args()
    
    if args.admin_username and args.admin_email and args.admin_password:
        create_admin_user(args.admin_username, args.admin_email, args.admin_password)
    else:
        run_migrations(args.admin_only, args.buses_only) 