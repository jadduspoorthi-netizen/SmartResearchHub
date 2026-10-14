from source_code.database.connection import get_connection


def get_chunks_by_paper_id(
    paper_id: int,
) -> list[dict]:
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                paper_id,
                chunk_index,
                content
            FROM paper_chunks
            WHERE paper_id = %s
            ORDER BY chunk_index;
            """,
            (paper_id,),
        )

        rows = cursor.fetchall()

        return [
            {
                "id": row[0],
                "paper_id": row[1],
                "chunk_index": row[2],
                "content": row[3],
            }
            for row in rows
        ]

    finally:
        connection.close()


def delete_chunks_by_paper_id(
    paper_id: int,
) -> int:
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM paper_chunks
            WHERE paper_id = %s;
            """,
            (paper_id,),
        )

        deleted_count = cursor.rowcount

        connection.commit()

        return deleted_count

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def count_chunks_by_paper_id(
    paper_id: int,
) -> int:
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM paper_chunks
            WHERE paper_id = %s;
            """,
            (paper_id,),
        )

        return int(cursor.fetchone()[0])

    finally:
        connection.close()


if __name__ == "__main__":
    print(
        "Chunk repository is ready."
    )
