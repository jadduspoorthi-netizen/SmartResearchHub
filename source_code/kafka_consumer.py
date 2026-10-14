import json
import os
import time
from typing import Any

from dotenv import load_dotenv
from kafka import KafkaConsumer


load_dotenv()


KAFKA_BOOTSTRAP_SERVERS = os.getenv(
    "KAFKA_BOOTSTRAP_SERVERS",
    "localhost:9092",
)

KAFKA_TOPIC = os.getenv(
    "KAFKA_TOPIC",
    "paper-events",
)

KAFKA_GROUP_ID = os.getenv(
    "KAFKA_GROUP_ID",
    "smartresearch-hub-consumer",
)


def create_kafka_consumer() -> KafkaConsumer:
    """
    Create a Kafka consumer configured for JSON events.
    """

    return KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=KAFKA_GROUP_ID,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda value: json.loads(
            value.decode("utf-8")
        ),
    )


def validate_paper_event(
    event: Any,
) -> bool:
    """
    Validate the basic structure of a paper event.
    """

    if not isinstance(event, dict):
        return False

    event_type = event.get(
        "event_type"
    )

    if event_type != "paper_uploaded":
        return False

    paper_id = event.get(
        "paper_id"
    )

    title = event.get(
        "title"
    )

    if not isinstance(
        paper_id,
        int,
    ):
        return False

    if not isinstance(
        title,
        str,
    ) or not title.strip():
        return False

    return True


def handle_paper_uploaded(
    event: dict,
) -> None:
    """
    Handle a paper-upload event.

    Heavy ingestion work is performed by the main
    ingestion pipeline; this consumer currently
    provides reliable event processing/logging.
    """

    paper_id = event["paper_id"]
    title = event["title"]
    filename = event.get(
        "filename"
    )

    print(
        "\nPaper upload event received."
    )

    print(
        f"Paper ID: {paper_id}"
    )

    print(
        f"Title: {title}"
    )

    if filename:
        print(
            f"Filename: {filename}"
        )


def process_event(
    event: Any,
) -> None:
    """
    Validate and route one Kafka event.
    """

    if not validate_paper_event(
        event
    ):
        print(
            "Invalid or unsupported Kafka event:"
        )
        print(event)
        return

    event_type = event.get(
        "event_type"
    )

    if event_type == "paper_uploaded":
        handle_paper_uploaded(
            event
        )


def run_consumer() -> None:
    """
    Continuously consume paper events.
    """

    print(
        "Starting SmartResearch Hub Kafka consumer..."
    )

    while True:
        consumer = None

        try:
            consumer = create_kafka_consumer()

            print(
                f"Listening on topic: "
                f"{KAFKA_TOPIC}"
            )

            for message in consumer:
                process_event(
                    message.value
                )

        except KeyboardInterrupt:
            print(
                "\nKafka consumer stopped."
            )
            break

        except Exception as error:
            print(
                "Kafka consumer error:"
            )
            print(error)

            print(
                "Retrying in 5 seconds..."
            )

            time.sleep(5)

        finally:
            if consumer is not None:
                try:
                    consumer.close()
                except Exception:
                    pass


if __name__ == "__main__":
    run_consumer()
