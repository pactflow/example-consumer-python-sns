import logging
import json
import asyncio
from typing import Dict
from src.product.product_service import receive_product_update
logger = logging.getLogger(__name__)


# Actual lambda handler, responsible for extracting message from SNS
# and dealing with lambda-related things, passing the encoded message along to the
# message handler
async def handler(event: Dict, context):
    logger.info(f'{event=}')

    # Read the SNS message and pass the contents to the actual message handler
    message: Dict = json.loads(event['Records'][0]['Sns']['Message'])
    logger.info(message)
    results = await receive_product_update(message)
    logger.info(results)

    # Return the current size of the repository
    return len(results.keys())

def lambda_handler(event, context):
    loop = asyncio.get_event_loop()
    # DynamoDB resource defined above is attached to this loop:
    #   if you use asyncio.run instead
    #   you will encounter "Event loop closed" exception
    return loop.run_until_complete(handler(event, context))