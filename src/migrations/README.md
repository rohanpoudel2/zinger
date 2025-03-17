# Database Migrations

This directory contains scripts for managing the database schema.

## Reset Database Approach

We use a "reset" approach for database migrations. Instead of creating incremental migration scripts, we reset the entire database when schema changes are needed. This approach is simpler and avoids migration conflicts.

## Available Scripts

### reset_database.py

This script drops all tables and recreates them with the latest schema. Use this when you need to update the database schema:

```bash
export PYTHONPATH=src:$PYTHONPATH
python src/migrations/reset_database.py
```

### populate_buses.py

This script populates the database with initial bus data from the CTTransit API:

```bash
export PYTHONPATH=src:$PYTHONPATH
python src/migrations/populate_buses.py
```

### create_admin.py

This script creates an admin user in the database:

```bash
export PYTHONPATH=src:$PYTHONPATH
python src/migrations/create_admin.py
```

## When to Use Reset

Use the reset approach when:

1. You add new fields to a model
2. You change field types
3. You add or modify relationships between models
4. You add new models

Note that resetting the database will delete all existing data. In a production environment, you would need to implement a data backup and restoration strategy.

## Database Schema

The current database schema includes the following tables:

- `users`: User accounts
- `buses`: Bus information
- `routes`: Route information
- `bookings`: User bookings

See the `models/database_models.py` file for the complete schema definition. 