import sys
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

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_migration.py <migration_file.sql>")
        sys.exit(1)
    migration_file = sys.argv[1]
    run_migration(migration_file)