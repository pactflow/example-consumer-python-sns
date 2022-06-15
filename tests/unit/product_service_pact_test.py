import os

import pytest as pytest
from pact import Like, MessageConsumer, Provider, Term

from src.product.product_service import receive_product_update

CONSUMER_NAME = "pactflow-example-consumer-python-sns"
PROVIDER_NAME = os.getenv("PACT_PROVIDER", "pactflow-example-provider-python-sns")
PACT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "pacts")

@pytest.fixture(scope="session")
def consumer():
    return receive_product_update


@pytest.fixture(scope="session")
def pact():
    pact = MessageConsumer(
        CONSUMER_NAME,
    ).has_pact_with(
        Provider(PROVIDER_NAME),
        pact_dir=PACT_DIR,
    )

    yield pact

@pytest.mark.asyncio
async def test_receive_a_product_update(pact, consumer):
    event = {
        "id": Like("some-uuid-1234-5678"),
        "type": Like("Product Range"),
        "name": Like("Some Product"),
        "event": Term(matcher="^(CREATED|UPDATED|DELETED)$", generate="UPDATED")
    }
    (
        pact
        .expects_to_receive("a product event update")
        .with_content(event)
        .with_metadata({"Content-Type": "application/json", 'topic': 'products'})
    )

    with pact:
        await consumer(event)
