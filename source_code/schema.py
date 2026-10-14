
from source_code.database.connection import get_connection


def initialize_schema():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            # Users table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(100) NOT NULL UNIQUE,
                    email VARCHAR(255) UNIQUE,
                    password_hash TEXT NOT NULL,
                    role VARCHAR(20) NOT NULL DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

            # Add email column to older users tables
            cursor.execute(
                """
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS email VARCHAR(255);
                """
            )

            # Unique email index
            cursor.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS
                users_email_unique_idx
                ON users (LOWER(email))
                WHERE email IS NOT NULL;
                """
            )

            # Add free/premium plan to each user
            cursor.execute(
                """
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS plan VARCHAR(20)
                NOT NULL DEFAULT 'free';
                """
            )

            # Papers table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS papers (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    authors TEXT,
                    abstract TEXT,
                    domain TEXT,
                    year INTEGER,
                    filename TEXT,
                    file_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

            # Upgrade older papers tables
            cursor.execute(
                """
                ALTER TABLE papers
                ADD COLUMN IF NOT EXISTS filename TEXT;
                """
            )

            cursor.execute(
                """
                ALTER TABLE papers
                ADD COLUMN IF NOT EXISTS file_path TEXT;
                """
            )

            cursor.execute(
                """
                ALTER TABLE papers
                ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP;
                """
            )

            # Paper chunks table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS paper_chunks (
                    id SERIAL PRIMARY KEY,
                    paper_id INTEGER NOT NULL
                        REFERENCES papers(id)
                        ON DELETE CASCADE,
                    chunk_index INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    embedding VECTOR(384)
                );
                """
            )

            # Index for paper chunks
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS
                paper_chunks_paper_id_idx
                ON paper_chunks (paper_id);
                """
            )

            # Daily paper search usage
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS daily_usage (
                    user_id INTEGER NOT NULL
                        REFERENCES users(id)
                        ON DELETE CASCADE,
                    usage_date DATE NOT NULL DEFAULT CURRENT_DATE,
                    search_count INTEGER NOT NULL DEFAULT 0
                        CHECK (search_count >= 0),
                    PRIMARY KEY (user_id, usage_date)
                );
                """
            )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    initialize_schema()
    print("Database schema initialized successfully.")
