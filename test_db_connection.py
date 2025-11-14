"""
Test script to verify database connection.
Run with: uv run python test_db_connection.py
"""

import asyncio

from sqlalchemy import text

from src.core.database.session import engine


async def test_connection():
    """Test database connection."""
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print("✓ Successfully connected to PostgreSQL!")
            print(f"  Version: {version}")

            # Test creating the database if it doesn't exist
            await conn.execute(text("SELECT 1"))
            print("✓ Database queries working!")

        return True
    except Exception as e:
        print(f"✗ Failed to connect to PostgreSQL")
        print(f"  Error: {e}")
        print(f"\nMake sure PostgreSQL is running and DATABASE_URL is correct.")
        print(f"Current DATABASE_URL: {engine.url}")
        return False
    finally:
        await engine.dispose()


if __name__ == "__main__":
    success = asyncio.run(test_connection())
    exit(0 if success else 1)
