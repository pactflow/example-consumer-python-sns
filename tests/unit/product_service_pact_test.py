import os

import pytest as pytest
import json
from pact.v3.pact import Pact
from pact import matchers
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
)
from src.product.product_service import receive_product_update
from src.product.product import Products

CONSUMER_NAME = "pactflow-example-consumer-python-sns"
PROVIDER_NAME = os.getenv("PACT_PROVIDER", "pactflow-example-provider-js-sns")
PACT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)),"..","..", "pacts")

@pytest.fixture(scope="module")
def handler():
    return receive_product_update

@pytest.fixture(scope="module")
def pact():
    pact_dir = Path(Path(__file__).parent.parent.parent / "pacts")
    pact = Pact(CONSUMER_NAME, PROVIDER_NAME)
    yield pact.with_specification("V3")
    pact.write_file(pact_dir, overwrite=True)

@pytest.fixture
def verifier(
    handler,
):
    """
    Verifier function for the Pact.

    This function is passed to the `verify` method of the Pact object. It is
    responsible for taking in the messages (along with the context/metadata)
    and ensuring that the consumer is able to process the message correctly.

    In our case, we deserialize the message and pass it to our message
    handler for processing.
    """

    def _verifier(msg: str | bytes | None, context: dict[str, Any]) -> None:
        assert msg is not None, "Message is None"
        data = json.loads(msg)
        print(
            "Processing message: ",
            {"input": msg, "processed_message": data, "context": context},
        )
        handler(data)
    yield _verifier

@pytest.mark.asyncio
async def test_receive_a_product_update(pact, handler, verifier):
    event = {
        "id": "some-uuid-1234-5678",
        "type": "Product Range",
        "name": "Some Product",
        "event": "UPDATED"
    }
    (
        pact
        .upon_receiving("a product event update", "Async")
        .with_body(json.dumps(event),
            "application/json")
        .with_matching_rules(
            {
                "body": {
                    "$.event": {
                        "combine": "AND",
                        "matchers": [
                        {
                            "match": "regex",
                            "regex": "^(CREATED|UPDATED|DELETED)$"
                        }
                        ]
                    },
                    "$.id": {
                        "combine": "AND",
                        "matchers": [
                        {
                            "match": "type"
                        }
                        ]
                    },
                    "$.name": {
                        "combine": "AND",
                        "matchers": [
                        {
                            "match": "type"
                        }
                        ]
                    },
                    "$.type": {
                        "combine": "AND",
                        "matchers": [
                        {
                            "match": "type"
                        }
                        ]
                    },
                    "$.version": {
                        "combine": "AND",
                        "matchers": [
                        {
                            "match": "type"
                        }
                        ]
                    }
                }
            }
        )
        .with_metadata({"topic": "products"})
    )
    pact.verify(verifier, "Async")