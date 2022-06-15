import json

import pytest

from src.product.product_repository import ProductRepository
from src._lambda import product


@pytest.mark.asyncio
async def test_lambda_consumes_a_valid_sns_event(mocker):
    # (1) Arrange
    # First we want mock out the actual low level handling code
    # we want to test the lambda interface here is plumbed correctly to the implementation code
    spy = mocker.spy(product, 'handler')
    repository = ProductRepository()
    num_products = len(await repository.fetch_all())

    # This is an example SNS message we can use to test the interface
    with open('tests/resources/events/update.json') as f:
        payload = json.load(f)

    # (2) Act: call the actual lambda with a valid SNS message
    result = await product.handler(payload)

    # (3) Assert: should return
    assert result == num_products + 1

    # Assert: check that the implementation code was invoked
    # if it gets here, it also meant it didn't encounter any issues
    assert spy.call_count == 1