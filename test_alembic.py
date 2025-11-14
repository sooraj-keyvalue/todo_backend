"""Test script to verify Alembic is working."""

import asyncio

from sqlalchemy import text

from src.core.database.session import engine


async def check_alembic():
    """Check if alembic version table exists."""
    try:
        async with engine.begin() as conn:
            result = await conn.execute(
                text("SELECT version_num FROM alembic_version")
            )
            rows = result.fetchall()
            
            print("✓ Alembic version table exists")
            if rows and rows[0][0]:
                print(f"  Current version: {rows[0][0]}")
            else:
                print("  Current version: (empty - no migrations yet)")
            
            return True
    except Exception as e:
        print(f"✗ Failed to check alembic version")
        print(f"  Error: {e}")
        return False
    finally:
        await engine.dispose()


if __name__ == "__main__":
    success = asyncio.run(check_alembic())
    exit(0 if success else 1)
