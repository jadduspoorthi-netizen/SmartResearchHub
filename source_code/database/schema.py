from source_code.database.connection import get_connection


EMBEDDING_DIMENSION = 384


def create_schema():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        # Enable pgvector.
        cursor.execute(
            "CREATE EXTENSION IF NOT EXISTS vector;"
        )

        # Users table.
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                CONSTRAINT users_role_check
                CHECK (role IN ('user', 'admin'))
            );
            """
        )

        # Papers table.
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS papers (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                authors TEXT,
                domain VARCHAR(100),
                year INTEGER,
                filename TEXT,
                file_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        # Paper chunks.
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS paper_chunks (
                id SERIAL PRIMARY KEY,
                paper_id INTEGER NOT NULL,
                chunk_index INTEGER NOT NULL,
                content TEXT NOT NULL,

                CONSTRAINT paper_chunks_paper_fk
                FOREIGN KEY (paper_id)
                REFERENCES papers(id)
                ON DELETE CASCADE,

                CONSTRAINT paper_chunks_unique
                UNIQUE (paper_id, chunk_index)
            );
            """
        )

        # Embeddings.
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS paper_embeddings (
                id SERIAL PRIMARY KEY,
                chunk_id INTEGER NOT NULL,
                embedding VECTOR({EMBEDDING_DIMENSION}) NOT NULL,

                CONSTRAINT paper_embeddings_chunk_fk
                FOREIGN KEY (chunk_id)
                REFERENCES paper_chunks(id)
                ON DELETE CASCADE,

                CONSTRAINT paper_embeddings_unique
                UNIQUE (chunk_id)
            );
            """
        )

        # Useful indexes.
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_papers_domain
            ON papers(domain);
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_papers_year
            ON papers(year);
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_paper_chunks_paper_id
            ON paper_chunks(paper_id);
            """
        )

        connection.commit()

        print("Database schema created successfully.")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    create_schema()
