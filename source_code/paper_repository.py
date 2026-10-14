from typing import Optional

from source_code.database.connection import get_connection


def create_paper(
    title: str,
    authors: Optional[str],
    domain: Optional[str],
    year: Optional[int],
    filename: Optional[str],
    file_path: Optional[str],
) -> int:
    """
    Create a paper record and return its database ID.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO papers (
                title,
                authors,
                domain,
                year,
                filename,
                file_path
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id;
            """,
            (
                title,
                authors,
                domain,
                year,
                filename,
                file_path,
            ),
        )

        paper_id = cursor.fetchone()[0]

        connection.commit()

        return paper_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_paper_by_id(
    paper_id: int,
) -> Optional[dict]:
    """
    Retrieve one paper by ID.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                title,
                authors,
                domain,
                year,
                filename,
                file_path,
                created_at,
                updated_at
            FROM papers
            WHERE id = %s;
            """,
            (paper_id,),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return {
            "id": row[0],
            "title": row[1],
            "authors": row[2],
            "domain": row[3],
            "year": row[4],
            "filename": row[5],
            "file_path": row[6],
            "created_at": row[7],
            "updated_at": row[8],
        }

    finally:
        connection.close()


def get_all_papers(
    search: Optional[str] = None,
    domain: Optional[str] = None,
    year: Optional[int] = None,
) -> list[dict]:
    """
    Retrieve papers for the repository.

    Supports optional title/author search,
    domain filtering, and year filtering.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        query = """
            SELECT
                id,
                title,
                authors,
                domain,
                year,
                filename,
                file_path,
                created_at,
                updated_at
            FROM papers
            WHERE 1 = 1
        """

        parameters = []

        if search:
            query += """
                AND (
                    title ILIKE %s
                    OR authors ILIKE %s
                )
            """

            search_pattern = f"%{search}%"

            parameters.extend(
                [
                    search_pattern,
                    search_pattern,
                ]
            )

        if domain:
            query += """
                AND domain = %s
            """

            parameters.append(domain)

        if year is not None:
            query += """
                AND year = %s
            """

            parameters.append(year)

        query += """
            ORDER BY created_at DESC, id DESC;
        """

        cursor.execute(
            query,
            parameters,
        )

        rows = cursor.fetchall()

        return [
            {
                "id": row[0],
                "title": row[1],
                "authors": row[2],
                "domain": row[3],
                "year": row[4],
                "filename": row[5],
                "file_path": row[6],
                "created_at": row[7],
                "updated_at": row[8],
            }
            for row in rows
        ]

    finally:
        connection.close()


def get_domains() -> list[str]:
    """
    Return all distinct paper domains.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT DISTINCT domain
            FROM papers
            WHERE domain IS NOT NULL
              AND TRIM(domain) <> ''
            ORDER BY domain;
            """
        )

        rows = cursor.fetchall()

        return [
            row[0]
            for row in rows
        ]

    finally:
        connection.close()


def paper_title_exists(
    title: str,
    exclude_paper_id: Optional[int] = None,
) -> bool:
    """
    Check whether a paper title already exists.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        if exclude_paper_id is None:
            cursor.execute(
                """
                SELECT 1
                FROM papers
                WHERE LOWER(TRIM(title))
                    = LOWER(TRIM(%s))
                LIMIT 1;
                """,
                (title,),
            )

        else:
            cursor.execute(
                """
                SELECT 1
                FROM papers
                WHERE LOWER(TRIM(title))
                    = LOWER(TRIM(%s))
                  AND id <> %s
                LIMIT 1;
                """,
                (
                    title,
                    exclude_paper_id,
                ),
            )

        return cursor.fetchone() is not None

    finally:
        connection.close()


def update_paper(
    paper_id: int,
    title: Optional[str] = None,
    authors: Optional[str] = None,
    domain: Optional[str] = None,
    year: Optional[int] = None,
) -> Optional[dict]:
    """
    Update paper metadata.
    """

    current = get_paper_by_id(
        paper_id
    )

    if current is None:
        return None

    new_title = (
        title
        if title is not None
        else current["title"]
    )

    new_authors = (
        authors
        if authors is not None
        else current["authors"]
    )

    new_domain = (
        domain
        if domain is not None
        else current["domain"]
    )

    new_year = (
        year
        if year is not None
        else current["year"]
    )

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE papers
            SET
                title = %s,
                authors = %s,
                domain = %s,
                year = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING
                id,
                title,
                authors,
                domain,
                year,
                filename,
                file_path,
                created_at,
                updated_at;
            """,
            (
                new_title,
                new_authors,
                new_domain,
                new_year,
                paper_id,
            ),
        )

        row = cursor.fetchone()

        connection.commit()

        if row is None:
            return None

        return {
            "id": row[0],
            "title": row[1],
            "authors": row[2],
            "domain": row[3],
            "year": row[4],
            "filename": row[5],
            "file_path": row[6],
            "created_at": row[7],
            "updated_at": row[8],
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def delete_paper(
    paper_id: int,
) -> bool:
    """
    Delete a paper.

    Related chunks and embeddings are automatically
    deleted through the database foreign-key cascade.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM papers
            WHERE id = %s;
            """,
            (paper_id,),
        )

        deleted = cursor.rowcount > 0

        connection.commit()

        return deleted

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def create_chunks_and_embeddings(
    paper_id: int,
    chunks: list[str],
    embeddings,
) -> int:
    """
    Store paper chunks and their vector embeddings.

    Returns the number of stored chunks.
    """

    if len(chunks) != len(embeddings):
        raise ValueError(
            "Chunk count and embedding count must match."
        )

    connection = get_connection()

    try:
        cursor = connection.cursor()

        inserted_count = 0

        for chunk_index, (
            content,
            embedding,
        ) in enumerate(
            zip(
                chunks,
                embeddings,
            )
        ):
            cursor.execute(
                """
                INSERT INTO paper_chunks (
                    paper_id,
                    chunk_index,
                    content
                )
                VALUES (%s, %s, %s)
                RETURNING id;
                """,
                (
                    paper_id,
                    chunk_index,
                    content,
                ),
            )

            chunk_id = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO paper_embeddings (
                    chunk_id,
                    embedding
                )
                VALUES (%s, %s::vector);
                """,
                (
                    chunk_id,
                    embedding.tolist(),
                ),
            )

            inserted_count += 1

        connection.commit()

        return inserted_count

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()
