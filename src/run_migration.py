import sys
import os
import glob
from db_functions import get_connection

def run_migration(migration_path):
    with open(migration_path, "r") as f:
        sql = f.read()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()
    print(f"Migration {migration_path} applied successfully.")

def run_all_migrations():
    """Run all migration files in the migrations directory in numerical order"""
    migrations_dir = "../migrations"
    if not os.path.exists(migrations_dir):
        print("No migrations directory found.")
        return
    
    # Get all .sql files in migrations directory and sort them
    migration_files = glob.glob(os.path.join(migrations_dir, "*.sql"))
    migration_files.sort()  # This will sort by filename, which should be in order due to numbering
    
    if not migration_files:
        print("No migration files found.")
        return
    
    print(f"Found {len(migration_files)} migration(s) to run:")
    for migration_file in migration_files:
        print(f"  - {os.path.basename(migration_file)}")
    
    print("\nRunning migrations...")
    for migration_file in migration_files:
        try:
            run_migration(migration_file)
        except Exception as e:
            print(f"Error running migration {migration_file}: {e}")
            print("Migration process stopped.")
            return
    
    print("\n✅ All migrations completed successfully!")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_migration.py <migration_file.sql>")
        sys.exit(1)
    migration_file = sys.argv[1]
    run_migration(migration_file)