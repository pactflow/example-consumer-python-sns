#!/usr/bin/env python
import logging
import asyncio
import json
from confluent_kafka import Consumer
from typing import Dict
from src.product.product_service import receive_product_update
logger = logging.getLogger(__name__)

def message_handler(event):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(handler(event))

async def handler(event: Dict):

    logger.info(f'{event=}')

    # Read the SNS message and pass the contents to the actual message handler
    message: Dict = json.loads(event.value().decode('utf-8'))
    logger.info(message)
    results = await receive_product_update(message)
    logger.info(results)

    # Return the current size of the repository
    return len(results.keys())


def consume_messages():
    config = {
        'bootstrap.servers': 'localhost:9092',
        'group.id':          'pactflow-example-consumer-python-kafka',
    }

    # Create Consumer instance
    consumer = Consumer(config)

    # Subscribe to topic
    topic = "products"
    consumer.subscribe([topic])

    # Poll for new messages from Kafka and print them.
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                print("Waiting...")
            elif msg.error():
                print("ERROR: %s".format(msg.error()))
            else:
                print("Consumed event from topic {topic}: value = {value:12}".format(
                    topic=msg.topic(), value=msg.value().decode('utf-8')))
                message_handler(msg)
    except KeyboardInterrupt:
        pass
    finally:
        # Leave group and commit final offsets
        consumer.close()
