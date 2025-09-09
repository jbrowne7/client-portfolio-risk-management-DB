from db_functions import get_connection

def reset_db():
    conn = get_connection()
    cur = conn.cursor()

    # Disable foreign key checks to be able to delete data
    cur.execute("SET session_replication_role = 'replica';")

    # Need to list tables in correct order (child tables first)
    tables = ["trades", "prices", "portfolios", "assets", "clients"]

    for table in tables:
        cur.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;")

    # Enable foreign key checks again
    cur.execute("SET session_replication_role = 'origin';")
    conn.commit()
    cur.close()
    conn.close()
    print("Database reset: all data deleted and sequences reset.")

if __name__ == "__main__":
    reset_db()