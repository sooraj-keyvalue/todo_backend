# Database Setup Guide

## Option 1: Using Docker Compose (Recommended)

Start the PostgreSQL container:

```bash
docker-compose up -d postgres
```

Check if it's running:

```bash
docker-compose ps
```

Stop the database:

```bash
docker-compose down
```

## Option 2: Using Existing PostgreSQL

If you have PostgreSQL already installed or running, update your `.env` file:

```env
DATABASE_URL=postgresql+asyncpg://your_user:your_password@localhost:5432/todo_db
```

Create the database:

```bash
# Using psql
psql -U postgres -c "CREATE DATABASE todo_db;"

# Or using Docker
docker exec -it your_postgres_container psql -U postgres -c "CREATE DATABASE todo_db;"
```

## Testing the Connection

Run the test script:

```bash
uv run python test_db_connection.py
```

Expected output:
```
✓ Successfully connected to PostgreSQL!
  Version: PostgreSQL 16.x ...
✓ Database queries working!
```

## Default Configuration

The default `.env` configuration expects:
- **Host**: localhost
- **Port**: 5432
- **User**: postgres
- **Password**: postgres
- **Database**: todo_db

## Troubleshooting

### Port 5432 already in use

If you have another PostgreSQL instance running on port 5432, either:

1. Stop the other instance
2. Change the port in `docker-compose.yml` and `.env`:
   ```yaml
   # docker-compose.yml
   ports:
     - "5433:5432"  # Use port 5433 on host
   ```
   ```env
   # .env
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/todo_db
   ```

### Connection refused

Make sure PostgreSQL is running:
```bash
docker-compose ps
```

### Authentication failed

Verify the credentials in your `.env` file match the PostgreSQL configuration.
