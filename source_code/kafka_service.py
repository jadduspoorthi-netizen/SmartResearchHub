import json
import os
from typing import Any, Optional

from dotenv import load_dotenv
from kafka import KafkaProducer


load_dotenv()


KAFKA_BOOTSTRAP_SERVERS = os.getenv(
    "KAFKA_BOOTSTRAP_SERVERS",
    "localhost:9092",
)

KAFKA_TOPIC = os.getenv(
    "KAFKA_TOPIC",
    "paper-events",
)


_producer: Optional[KafkaProducer] = None


def get_producer() -> KafkaProducer:
    """
    Create and cache the Kafka producer.
    """

    global _producer

    if _producer is None:
        _producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda value: json.dumps(
                value
            ).encode("utf-8"),
            retries=3,
            acks="all",
        )

    return _producer


def publish_event(
    event: dict[str, Any],
) -> Optional[dict]:
    """
    Publish an event to Kafka.

    Returns event delivery information when Kafka
    is available. Returns None when Kafka cannot
    currently be reached.
    """

    if not isinstance(event, dict):
        raise TypeError(
            "Kafka event must be a dictionary."
        )

    try:
        producer = get_producer()

        future = producer.send(
            KAFKA_TOPIC,
            event,
        )

        metadata = future.get(
            timeout=10
        )

        return {
            "topic": metadata.topic,
            "partition": metadata.partition,
            "offset": metadata.offset,
        }

    except Exception as error:
        print(
            "Kafka publish skipped:",
            error,
        )

        return None


def publish_paper_uploaded(
    paper_id: int,
    title: str,
    filename: Optional[str] = None,
) -> Optional[dict]:
    """
    Publish a paper-uploaded event.
    """

    event = {
        "event_type": "paper_uploaded",
        "paper_id": paper_id,
        "title": title,
        "filename": filename,
    }

    return publish_event(event)


def close_producer() -> None:
    """
    Flush and close the Kafka producer.
    """

    global _producer

    if _producer is not None:
        try:
            _producer.flush()
            _producer.close()
        finally:
            _producer = None


if __name__ == "__main__":
    result = publish_paper_uploaded(
        paper_id=1,
        title="Kafka connectivity test",
        filename="test.pdf",
    )

    if result:
        print(
            "Kafka event published:",
            result,
        )
    else:
        print(
            "Kafka is not currently available. "
            "The application can continue without it."
        )

    close_producer()
