import os, psycopg2
def test_db_connect():
    dsn = os.getenv("DATABASE_URL")
    assert dsn and dsn.startswith("postgresql")
    conn = psycopg2.connect(dsn.replace("+psycopg2", ""))
    with conn.cursor() as cur:
        cur.execute("SELECT 1")
        assert cur.fetchone()[0] == 1
    conn.close()
