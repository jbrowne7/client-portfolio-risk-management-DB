import os
import sys
from datetime import datetime

def create_migration_file(migration_name):
    migrations_dir = os.path.join("..", "migrations")
    os.makedirs(migrations_dir, exist_ok=True)

    existing = [f for f in os.listdir(migrations_dir) if f.endswith(".sql")]
    numbers = [int(f.split("_")[0]) for f in existing if f.split("_")[0].isdigit()]
    next_number = max(numbers, default=0) + 1
    filename = f"{next_number:03d}_{migration_name}.sql"
    filepath = os.path.join(migrations_dir, filename)
    print(filepath)

    with open(filepath, "w") as f:
        f.write(f"-- Migration: {migration_name}\n-- Created: {datetime.now()}\n\n-- Write your SQL changes below\n")
    print(f"Created migration file: {filepath}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_migration.py <migration_name>")
        sys.exit(1)
    migration_name = sys.argv[1]
    create_migration_file(migration_name)

